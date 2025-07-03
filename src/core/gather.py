"""
Módulo de coleta otimizado para SimpleMMO.
Versão melhorada com separação de responsabilidades e melhor performance.
"""

from dataclasses import dataclass
from enum import Enum
import random
import re
import time
import tkinter as tk
from typing import Any

from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from core.context import registrar_acao
from driver.actions import buscar_botao_por_texto, clicar_elemento, url_comeca_com
from driver.manager import get_driver
from utils.logger import inserir_log
from utils.timing import sleep_interrompivel

# ===============================
# CONSTANTES E ENUMS
# ===============================


class GatherStatus(Enum):
    """Status possíveis da coleta."""

    SUCCESS = "success"
    INSUFFICIENT_LEVEL = "insufficient_level"
    NO_MATERIALS = "no_materials"
    COMPLETED = "completed"
    ERROR = "error"
    TIMEOUT = "timeout"


class GatherType(Enum):
    """Tipos de coleta disponíveis."""

    CHOP = "chop"
    MINE = "mine"
    SALVAGE = "salvage"
    CATCH = "catch"


# ===============================
# CLASSES DE DADOS
# ===============================


@dataclass
class GatherState:
    """Estado atual da coleta."""

    materials_available: int | None = None
    materials_collected: int = 0
    status: GatherStatus = GatherStatus.SUCCESS
    is_gathering: bool = False
    last_gather_time: float = 0.0


@dataclass
class GatherConfig:
    """Configuração de coleta."""

    cooldown_time: float = 0.5
    max_wait_time: int = 6
    max_consecutive_failures: int = 3
    check_interval: float = 0.3


# ===============================
# ESTADO GLOBAL OTIMIZADO
# ===============================

_gather_state = GatherState()
_gather_config = GatherConfig()

# ===============================
# SELETORES XPATH CENTRALIZADOS
# ===============================


class XPathSelectors:
    """Centralizador de seletores XPath."""

    GATHER_BUTTON = (
        "//button[@id='crafting_button' and .//span[text()='Press here to gather']]"
    )
    CLOSE_BUTTON = "//button[.//span[text()='Press here to close']]"
    INSUFFICIENT_LEVEL = "//div[contains(@class, 'text-red-800') and contains(text(), 'Your skill level isn')]"
    AVAILABLE_AMOUNT = "//div[contains(@class, 'text-gray-500') and contains(@class, 'font-semibold') and @x-text='available_amount']"
    LEGACY_GATHER_BUTTON = "//button[.//span[contains(text(),'Press here to gather')]]"


# ===============================
# FUNÇÕES DE VERIFICAÇÃO OTIMIZADAS
# ===============================


def verificar_nivel_insuficiente() -> bool:
    """Verifica se o jogador não tem nível suficiente para a coleta."""
    driver = get_driver()
    if not driver:
        return False

    try:
        element = driver.find_element(By.XPATH, XPathSelectors.INSUFFICIENT_LEVEL)
        return element.is_displayed()
    except (NoSuchElementException, StaleElementReferenceException):
        return False


def obter_quantidade_disponivel() -> int | None:
    """Obtém a quantidade de materiais disponíveis com cache."""
    driver = get_driver()
    if not driver:
        return None

    try:
        element = driver.find_element(By.XPATH, XPathSelectors.AVAILABLE_AMOUNT)
        quantidade_text = element.text.strip()

        # Extrai números do texto
        numeros = re.findall(r"\d+", quantidade_text)
        return int(numeros[0]) if numeros else None

    except (NoSuchElementException, StaleElementReferenceException, ValueError):
        return None


def verificar_estado_botao_gather() -> tuple[bool, str]:
    """
    Verifica o estado do botão gather de forma otimizada.

    Returns:
        Tuple[bool, str]: (is_ready, reason)
    """
    driver = get_driver()
    if not driver:
        return False, "Driver não disponível"

    try:
        botao = driver.find_element(By.XPATH, XPathSelectors.GATHER_BUTTON)

        # Verificações em ordem de performance
        if not botao.is_displayed():
            return False, "Botão não visível"

        style_attr = botao.get_attribute("style") or ""
        if "display: none" in style_attr:
            return False, "Botão oculto (display: none)"

        if botao.get_attribute("disabled") in ["true", True]:
            return False, "Botão desabilitado"

        if not botao.is_enabled():
            return False, "Botão não habilitado"

        return True, "Pronto"

    except NoSuchElementException:
        return False, "Botão não encontrado"
    except Exception as e:
        return False, f"Erro: {type(e).__name__}"


def verificar_botao_close_disponivel() -> bool:
    """Verifica se o botão close está disponível de forma otimizada."""
    driver = get_driver()
    if not driver:
        return False

    try:
        botao = driver.find_element(By.XPATH, XPathSelectors.CLOSE_BUTTON)
        return botao.is_displayed() and botao.is_enabled()
    except (NoSuchElementException, StaleElementReferenceException):
        return False


# ===============================
# FUNÇÕES DE ESPERA OTIMIZADAS
# ===============================


def aguardar_botao_ficar_pronto(
    log_box: tk.Text | None = None, timeout_max: int | None = None
) -> tuple[bool, str]:
    """
    Aguarda o botão gather ficar pronto com verificações otimizadas.
    Aguarda pacientemente até o botão voltar a ficar disponível.

    Returns:
        Tuple[bool, str]: (success, reason)
    """
    if timeout_max is None:
        timeout_max = 20  # Aumentar timeout padrão para dar mais tempo

    inicio = time.time()
    tentativas = 0
    ultima_razao = ""

    inserir_log(
        log_box,
        f"⏳ Aguardando botão gather ficar disponível (máx {timeout_max}s)...",
        debug=True,
    )

    while (time.time() - inicio) < timeout_max:
        tentativas += 1

        # Verificação principal do botão gather PRIMEIRO
        is_ready, reason = verificar_estado_botao_gather()
        ultima_razao = reason

        if is_ready:
            tempo_decorrido = time.time() - inicio
            inserir_log(
                log_box,
                f"✅ Botão gather disponível após {tentativas} verificações ({tempo_decorrido:.1f}s)",
                debug=True,
            )
            return True, "Pronto"

        # Se botão desapareceu completamente, aguardar mais um pouco
        if "não encontrado" in reason:
            inserir_log(
                log_box,
                "🔍 Botão gather não encontrado - aguardando reaparecer...",
                debug=True,
            )
            sleep_interrompivel(1.0)
            continue

        # Verificação de materiais esgotados - APENAS após tentativas significativas
        if tentativas > 10:  # Só verificar após várias tentativas
            quantidade = obter_quantidade_disponivel()
            if quantidade is not None and quantidade == 0:
                inserir_log(
                    log_box,
                    "📦 Quantidade detectada como 0 - aguardando botão close...",
                    debug=True,
                )
                # Aguardar mais tempo para botão close aparecer
                for i in range(5):  # 5 tentativas de 1 segundo
                    sleep_interrompivel(1.0)
                    if verificar_botao_close_disponivel():
                        return False, "Materiais esgotados"
                    inserir_log(
                        log_box, f"   Aguardando botão close... ({i + 1}/5)", debug=True
                    )

        # Verificação se coleta foi finalizada (botão close apareceu) - ÚLTIMO
        if verificar_botao_close_disponivel():
            return False, "Coleta finalizada"

        sleep_interrompivel(_gather_config.check_interval)

    return False, f"Timeout após {timeout_max}s - última razão: {ultima_razao}"


# ===============================
# FUNÇÕES DE COLETA CORE
# ===============================


def executar_coleta_unica(
    log_box: tk.Text | None = None,
) -> tuple[bool, GatherStatus]:
    """
    Executa uma única coleta com verificações otimizadas.
    Assume que o botão já foi verificado e está pronto.

    Returns:
        Tuple[bool, GatherStatus]: (success, status)
    """
    global _gather_state

    driver = get_driver()
    if not driver:
        return False, GatherStatus.ERROR

    # Verificação de cooldown
    agora = time.time()
    if agora - _gather_state.last_gather_time < _gather_config.cooldown_time:
        inserir_log(log_box, "⏰ Aguardando cooldown", debug=True)
        return False, GatherStatus.TIMEOUT

    if _gather_state.is_gathering:
        inserir_log(log_box, "🔄 Coleta já em andamento", debug=True)
        return False, GatherStatus.ERROR

    _gather_state.is_gathering = True

    try:
        # 1. Verificações básicas apenas
        if verificar_nivel_insuficiente():
            return False, GatherStatus.INSUFFICIENT_LEVEL

        # 2. Buscar e clicar no botão (assume que já está pronto)
        try:
            botao = driver.find_element(By.XPATH, XPathSelectors.GATHER_BUTTON)

            # Verificação rápida antes do clique
            if not (botao.is_displayed() and botao.is_enabled()):
                inserir_log(log_box, "⚠️ Botão não está disponível no momento do clique")
                return False, GatherStatus.ERROR

            botao.click()
            _gather_state.last_gather_time = time.time()

            inserir_log(log_box, "✅ Clique no botão gather executado")
            registrar_acao("Coleta")

            # Aguarda processamento da coleta
            sleep_interrompivel(random.uniform(1.5, 2.5))

            return True, GatherStatus.SUCCESS

        except NoSuchElementException:
            inserir_log(log_box, "❌ Botão gather não encontrado no momento do clique")
            return False, GatherStatus.ERROR
        except Exception as e:
            inserir_log(log_box, f"⚠️ Erro ao clicar no botão: {type(e).__name__}")
            return False, GatherStatus.ERROR

    finally:
        _gather_state.is_gathering = False


def executar_coleta_completa(log_box: tk.Text | None = None) -> dict[str, Any]:
    """
    Executa coleta completa de todos os materiais disponíveis.
    Aguarda o botão ficar disponível após cada coleta e só para quando aparece 'Press here to close'.

    Returns:
        Dict com resultados da coleta
    """
    global _gather_state

    driver = get_driver()
    if not driver:
        return {"success": False, "materials_collected": 0, "status": "driver_error"}

    # Reset do estado
    _gather_state.materials_collected = 0
    _gather_state.materials_available = obter_quantidade_disponivel()

    if _gather_state.materials_available is not None:
        inserir_log(
            log_box, f"📦 {_gather_state.materials_available} materiais disponíveis"
        )
        max_coletas = _gather_state.materials_available + 5  # Margem de segurança
    else:
        inserir_log(
            log_box, "⚠️ Quantidade não detectada, coletando até botão close aparecer"
        )
        max_coletas = 100  # Limite muito alto, confiando no botão close

    inserir_log(
        log_box, "🔄 Iniciando coleta contínua - aguardando botão close aparecer"
    )

    # Loop de coleta aprimorado
    falhas_consecutivas = 0
    verificacoes_close_sem_sucesso = 0
    max_verificacoes_close = 5  # Máximo de verificações antes de forçar saída

    while falhas_consecutivas < _gather_config.max_consecutive_failures:
        # Verificar se alcançou limite máximo (segurança)
        if _gather_state.materials_collected >= max_coletas:
            inserir_log(
                log_box,
                f"⚠️ Limite máximo de coletas atingido ({max_coletas}) - verificando botão close final",
            )
            # Aguardar mais tempo para o botão close aparecer
            for i in range(8):  # 8 segundos de espera
                sleep_interrompivel(1.0)
                if verificar_botao_close_disponivel():
                    inserir_log(log_box, "🚪 Botão close encontrado após limite!")
                    break
                inserir_log(
                    log_box,
                    f"   Aguardando botão close após limite... ({i + 1}/8)",
                    debug=True,
                )
            break

        # Aguardar botão gather ficar disponível
        inserir_log(
            log_box,
            f"⏳ Aguardando botão gather ficar disponível (coleta {_gather_state.materials_collected + 1})...",
        )
        ready, reason = aguardar_botao_ficar_pronto(log_box, timeout_max=15)

        if not ready:
            if "Coleta finalizada" in reason or "Materiais esgotados" in reason:
                inserir_log(log_box, f"✅ {reason} - finalizando")
                break
            else:
                falhas_consecutivas += 1
                inserir_log(
                    log_box,
                    f"⚠️ Botão não ficou pronto: {reason} ({falhas_consecutivas}/{_gather_config.max_consecutive_failures})",
                )

                # Se falhou múltiplas vezes, verificar mais cuidadosamente se botão close apareceu
                if falhas_consecutivas >= 2:
                    inserir_log(
                        log_box, "🔍 Verificação extra do botão close após falhas..."
                    )
                    for i in range(3):
                        sleep_interrompivel(1.5)
                        if verificar_botao_close_disponivel():
                            inserir_log(
                                log_box,
                                "🚪 Botão close encontrado após verificação extra!",
                            )
                            falhas_consecutivas = 999  # Forçar saída do loop
                            break
                        inserir_log(
                            log_box,
                            f"   Verificação extra close... ({i + 1}/3)",
                            debug=True,
                        )

                if falhas_consecutivas < _gather_config.max_consecutive_failures:
                    sleep_interrompivel(2.0)
                continue

        # Executar uma coleta
        sucesso, status = executar_coleta_unica(log_box)

        if sucesso:
            _gather_state.materials_collected += 1
            falhas_consecutivas = 0
            verificacoes_close_sem_sucesso = 0
            inserir_log(
                log_box,
                f"📦 Material {_gather_state.materials_collected} coletado com sucesso",
            )

            # Aguardar um pouco após coleta bem-sucedida
            sleep_interrompivel(random.uniform(1.0, 1.5))

            # Verificação especial: se coletou muitos materiais, verificar se close apareceu
            if (
                _gather_state.materials_collected > 0
                and _gather_state.materials_collected % 5 == 0
            ):
                inserir_log(
                    log_box,
                    f"🔍 Verificação periódica do botão close ({_gather_state.materials_collected} coletados)...",
                )
                if verificar_botao_close_disponivel():
                    inserir_log(
                        log_box, "🚪 Botão close detectado na verificação periódica!"
                    )
                    break
        else:
            falhas_consecutivas += 1

            if status == GatherStatus.INSUFFICIENT_LEVEL:
                inserir_log(log_box, "❌ Nível insuficiente - parando coleta")
                break
            elif status == GatherStatus.COMPLETED:
                inserir_log(log_box, "✅ Coleta completada automaticamente")
                break
            elif status == GatherStatus.NO_MATERIALS:
                inserir_log(log_box, "📦 Sem materiais - aguardando botão close...")
                verificacoes_close_sem_sucesso += 1

                # Aguardar mais tempo quando detectar "sem materiais"
                for i in range(6):  # 6 segundos de espera
                    sleep_interrompivel(1.0)
                    if verificar_botao_close_disponivel():
                        inserir_log(
                            log_box,
                            "🚪 Botão close encontrado após detectar sem materiais!",
                        )
                        falhas_consecutivas = 999  # Forçar saída
                        break
                    inserir_log(
                        log_box,
                        f"   Aguardando close após sem materiais... ({i + 1}/6)",
                        debug=True,
                    )

                if verificacoes_close_sem_sucesso >= max_verificacoes_close:
                    inserir_log(
                        log_box,
                        "⚠️ Muitas verificações sem encontrar close - forçando saída",
                    )
                    break

            inserir_log(
                log_box,
                f"⚠️ Falha na coleta: {status} ({falhas_consecutivas}/{_gather_config.max_consecutive_failures})",
            )
            sleep_interrompivel(1.5)

    # Verificação final do botão close antes de finalizar
    inserir_log(log_box, "🔍 Verificação final do botão close...")
    for i in range(5):
        if verificar_botao_close_disponivel():
            inserir_log(log_box, "🚪 Botão close confirmado na verificação final!")
            break
        sleep_interrompivel(1.0)
        inserir_log(log_box, f"   Verificação final... ({i + 1}/5)", debug=True)

    # Finalização
    inserir_log(
        log_box,
        f"🔚 Finalizando coleta ({_gather_state.materials_collected} materiais)",
    )
    sleep_interrompivel(1)

    interface_fechada = fechar_interface_coleta()

    resultado = {
        "success": _gather_state.materials_collected > 0,
        "materials_collected": _gather_state.materials_collected,
        "materials_available": _gather_state.materials_available,
        "interface_closed": interface_fechada,
        "status": "completed",
    }

    if interface_fechada:
        inserir_log(
            log_box,
            f"🚪 Interface fechada após {_gather_state.materials_collected} coletas",
        )
    else:
        inserir_log(log_box, "⚠️ Falha ao fechar interface")

    return resultado


# ===============================
# FUNÇÕES DE INTERFACE
# ===============================


def fechar_interface_coleta() -> bool:
    """Fecha a interface de coleta com fallbacks e múltiplas tentativas."""
    driver = get_driver()
    if not driver:
        return False

    # Múltiplas tentativas para encontrar e clicar no botão close
    for tentativa in range(3):
        try:
            # Método principal: botão close
            btn_close = driver.find_element(By.XPATH, XPathSelectors.CLOSE_BUTTON)

            if btn_close.is_displayed() and btn_close.is_enabled():
                btn_close.click()
                sleep_interrompivel(2)

                # Verificar se realmente fechou (não está mais na página de gather)
                if not url_comeca_com(
                    "https://web.simple-mmo.com/crafting/material/gather/"
                ):
                    inserir_log(
                        None,
                        f"✅ Interface fechada com sucesso (tentativa {tentativa + 1})",
                        debug=True,
                    )
                    return True
                else:
                    inserir_log(
                        None,
                        f"⚠️ Clique realizado mas ainda na interface (tentativa {tentativa + 1})",
                        debug=True,
                    )
                    sleep_interrompivel(1)
                    continue
            else:
                inserir_log(
                    None,
                    f"⚠️ Botão close não disponível (tentativa {tentativa + 1})",
                    debug=True,
                )

        except NoSuchElementException:
            inserir_log(
                None,
                f"❌ Botão close não encontrado (tentativa {tentativa + 1})",
                debug=True,
            )

        # Aguardar antes da próxima tentativa
        if tentativa < 2:  # Não aguardar na última tentativa
            sleep_interrompivel(1.5)

    # Se chegou aqui, todas as tentativas falharam
    inserir_log(
        None,
        "❌ Todas as tentativas de fechar falharam, usando navegação forçada",
        debug=True,
    )

    # Fallback: navegação forçada
    try:
        driver.get("https://web.simple-mmo.com/travel")
        sleep_interrompivel(2)
        return True
    except Exception as e:
        inserir_log(None, f"❌ Erro na navegação forçada: {e}", debug=True)
        return False


# ===============================
# FUNÇÕES DE VERIFICAÇÃO NA PÁGINA PRINCIPAL
# ===============================


def verificar_gather_disponivel_pagina_principal():
    """Verifica se há botões de gather disponíveis na página principal."""
    from driver.actions import buscar_botao_por_texto
    from driver.manager import get_driver

    driver = get_driver()
    if not driver:
        return None

    # Lista de botões de gather possíveis
    botoes_gather = ["Chop", "Mine", "Salvage", "Catch"]

    try:
        for nome_botao in botoes_gather:
            botao = buscar_botao_por_texto(nome_botao)
            if botao:
                return nome_botao, botao
        return None
    except Exception:
        return None


# ===============================
# FUNÇÃO PRINCIPAL OTIMIZADA
# ===============================


def processar_botao_de_coleta(nome_botao: str, log_box: tk.Text | None = None) -> bool:
    """
    Processa um botão de coleta específico com otimizações.

    Args:
        nome_botao: Nome do botão de coleta (Chop, Mine, Salvage, Catch)
        log_box: Widget de log opcional

    Returns:
        bool: True se processou com sucesso
    """
    driver = get_driver()
    if not driver:
        return False

    # Evita processar se já estiver na interface
    if url_comeca_com("https://web.simple-mmo.com/crafting/material/gather/"):
        return False

    try:
        # 1. Busca e clica no botão
        botao = buscar_botao_por_texto(nome_botao)
        if not botao:
            return False

        inserir_log(log_box, f"⛏️ Iniciando coleta de {nome_botao}...")

        # Clique otimizado
        sucesso_clique = clicar_elemento(botao[0] if isinstance(botao, list) else botao)
        if not sucesso_clique:
            inserir_log(log_box, f"❌ Falha ao clicar em {nome_botao}")
            return False

        # 2. Aguarda entrada na interface com WebDriverWait
        try:
            WebDriverWait(driver, 7).until(
                lambda d: url_comeca_com(
                    "https://web.simple-mmo.com/crafting/material/gather/"
                )
            )
        except Exception:
            inserir_log(log_box, f"❌ Timeout: não entrou na interface de {nome_botao}")
            return False

        # 3. Aguarda carregamento completo
        sleep_interrompivel(1.5)

        # 4. Verificação de nível
        if verificar_nivel_insuficiente():
            inserir_log(log_box, f"❌ Nível insuficiente para {nome_botao}")
            fechar_interface_coleta()
            return True

        # 5. Executa coleta completa
        resultado = executar_coleta_completa(log_box)

        # 6. Atualiza estatísticas
        if resultado["success"]:
            nome_lower = nome_botao.lower()
            if nome_lower in [t.value for t in GatherType]:
                # Estatística removida temporariamente
                pass
            inserir_log(
                log_box,
                f"✅ Coleta de {nome_botao} concluída ({resultado['materials_collected']} materiais)",
            )

        return True

    except Exception as e:
        inserir_log(log_box, f"❌ Erro ao processar {nome_botao}: {e}")
        return False


# ===============================
# FUNÇÃO PRINCIPAL PARA BOT LOOP
# ===============================


def processar_coleta(log_box: tk.Text | None = None) -> bool:
    """
    Função principal de coleta chamada pelo bot_loop.
    Detecta e processa qualquer oportunidade de coleta na página atual.

    Args:
        log_box: Widget de log opcional

    Returns:
        bool: True se processou alguma coleta
    """
    # Verifica se já está em uma interface de coleta
    driver = get_driver()
    if not driver:
        return False

    # Se já estiver na interface de coleta, continue o processo
    if url_comeca_com("https://web.simple-mmo.com/crafting/material/gather/"):
        resultado = executar_coleta_completa(log_box)
        return resultado["success"]

    # Verifica botões disponíveis na página principal
    gather_info = verificar_gather_disponivel_pagina_principal()
    if gather_info:
        nome_botao, botao = gather_info
        return processar_botao_de_coleta(nome_botao, log_box)

    return False


# ===============================
# FUNÇÕES DE COMPATIBILIDADE
# ===============================


def coletar(driver, log_fn=print) -> bool:
    """Função original mantida para compatibilidade."""
    try:
        botao = driver.find_element(By.XPATH, XPathSelectors.LEGACY_GATHER_BUTTON)
        if botao.is_displayed() and botao.is_enabled():
            botao.click()
            registrar_acao("Coleta")
            log_fn("✅ Material coletado.")
            time.sleep(random.uniform(3, 5))
            # Estatística removida temporariamente
            return True
        return False
    except NoSuchElementException:
        log_fn("❌ Botão de coleta não encontrado.")
        return False
    except Exception as e:
        log_fn(f"⚠️ Erro ao coletar: {e}")
        return False


# Aliases para compatibilidade
coletar_material_unico = executar_coleta_unica
coletar_material = executar_coleta_completa
