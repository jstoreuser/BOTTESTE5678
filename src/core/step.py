"""Sistema de navegação SimpleMMO Bot - Passos (steps)"""

import random
import time
import tkinter as tk

from selenium.webdriver.common.by import By

from core.context import registrar_acao
from driver.actions import buscar_botao_por_texto, clicar_elemento
from driver.manager import get_driver
from utils.logger import inserir_log

# ===============================
# FUNÇÕES DE PASSO (STEP)
# ===============================


def tentar_passo(driver, log_fn=print) -> bool:
    """Função original mantida para compatibilidade."""
    try:
        log_fn(f"🌐 URL atual: {driver.current_url}")
        log_fn("🔍 Procurando botão 'Take a step'...")
        botoes = driver.find_elements(By.XPATH, "//button[contains(., 'Take a step')]")
        if not botoes:
            botoes = driver.find_elements(By.XPATH, "//a[contains(., 'Take a step')]")
        log_fn(f"Encontrados {len(botoes)} botões 'Take a step'.")
        for botao in botoes:
            log_fn(
                f"Botão exibido: {botao.is_displayed()}, habilitado: {botao.is_enabled()}"
            )
            if botao.is_displayed() and botao.is_enabled():
                delay = random.uniform(1.5, 2.5)
                log_fn(f"Aguardando {delay:.2f}s antes de clicar no botão.")
                time.sleep(delay)
                botao.click()
                registrar_acao("Passo")
                log_fn("✔ Passo realizado")
                return True
        log_fn("⏳ Nenhum botão de passo disponível para clicar.")
        return False
    except Exception as e:
        log_fn(f"⚠️ Erro ao tentar passo: {e}")
        return False


def tentar_passo_modular(log_box: tk.Text | None) -> bool:
    """Versão modular otimizada para tentar dar um passo - DETECÇÃO RÁPIDA."""
    driver = get_driver()
    if not driver:
        return False

    try:
        # Busca rápida usando buscar_botao_por_texto otimizado
        resultado = buscar_botao_por_texto("Take a step", todos=False)
        if not resultado:
            return False

        # Verifica se é uma lista ou um elemento único
        botao = resultado[0] if isinstance(resultado, list) else resultado

        # Clica no botão encontrado com delay mínimo
        if clicar_elemento(botao):
            inserir_log(log_box, "✔ Passo realizado", "info")
            registrar_acao("Passo")
            return True

        return False
    except Exception as e:
        inserir_log(log_box, f"⚠️ Erro ao tentar passo: {e}", "error")
        return False


def executar_step_interno(log_box: tk.Text | None) -> bool:
    """Executa um step internamente sem logging externo - OTIMIZADO."""
    driver = get_driver()
    if not driver:
        return False

    try:
        # Busca rápida usando buscar_botao_por_texto otimizado
        resultado = buscar_botao_por_texto("Take a step", todos=False)
        if not resultado:
            inserir_log(
                log_box,
                "🔍 Nenhum botão de step encontrado para execução interna",
                debug=True,
            )
            return False

        # Verifica se é uma lista ou um elemento único
        botao = resultado[0] if isinstance(resultado, list) else resultado

        # Clica no botão encontrado
        if clicar_elemento(botao):
            registrar_acao("Passo")
            inserir_log(log_box, "🚶‍♂️ Step interno executado com sucesso", debug=True)
            return True

        inserir_log(log_box, "❌ Falha ao clicar em botão de step interno", debug=True)
        return False
    except Exception as e:
        inserir_log(log_box, f"❌ Erro no step interno: {e}", debug=True)
        return False


def dar_step(log_box=None) -> bool:
    """Versão otimizada da função de dar passo - DETECÇÃO ULTRA-RÁPIDA COM DEBUG."""
    inserir_log(log_box, "🔍 Iniciando tentativa de dar step...", debug=True)

    # Primeira tentativa: função ultra-rápida
    inserir_log(log_box, "🚀 Tentando função rápida...", debug=True)
    if clicar_step_rapido(log_box):
        inserir_log(log_box, "✅ Step realizado pela função rápida", debug=True)
        return True

    inserir_log(log_box, "⚠️ Função rápida falhou, tentando fallback...", debug=True)

    # Fallback: versão original com delay reduzido
    try:
        driver = get_driver()
        if not driver:
            inserir_log(log_box, "❌ Driver não disponível")
            return False

        inserir_log(log_box, "🔍 Procurando botões Take a step...", debug=True)

        # Busca otimizada: primeiro tenta botões, depois links se necessário
        botoes = driver.find_elements(
            By.XPATH, "//button[contains(., 'Take a step')]"
        ) or driver.find_elements(By.XPATH, "//a[contains(., 'Take a step')]")

        inserir_log(log_box, f"📊 Encontrados {len(botoes)} elementos", debug=True)

        # Verifica apenas os primeiros 2 elementos para acelerar
        for i, botao in enumerate(botoes[:2]):
            try:
                is_displayed = botao.is_displayed()
                is_enabled = botao.is_enabled()
                text = botao.text.strip() if hasattr(botao, "text") else "N/A"

                inserir_log(
                    log_box,
                    f"🔍 Elemento {i + 1}: '{text}' (display: {is_displayed}, enabled: {is_enabled})",
                    debug=True,
                )

                if is_displayed and is_enabled:
                    # Delay mínimo - apenas o necessário para parecer humano
                    delay = random.uniform(0.3, 0.7)
                    inserir_log(
                        log_box,
                        f"⏰ Aguardando {delay:.2f}s antes do clique...",
                        debug=True,
                    )
                    time.sleep(delay)

                    botao.click()
                    registrar_acao("Passo")
                    inserir_log(log_box, "✔ Passo realizado (fallback)")
                    return True
                else:
                    inserir_log(
                        log_box,
                        f"❌ Elemento {i + 1} não disponível para clique",
                        debug=True,
                    )
            except Exception as e:
                inserir_log(log_box, f"❌ Erro no elemento {i + 1}: {e}", debug=True)
                continue  # Tenta próximo botão se este falhar

        inserir_log(log_box, "⏳ Nenhum botão de passo disponível")
        return False
    except Exception as e:
        inserir_log(log_box, f"⚠️ Erro ao dar passo: {e}")
        return False


def navegar_para_travel(log_box=None) -> None:
    """Navega para a página de travel."""
    try:
        driver = get_driver()
        if not driver:
            inserir_log(log_box, "❌ Driver não disponível")
            return

        inserir_log(log_box, "🧭 Navegando para travel...")
        driver.get("https://web.simple-mmo.com/travel")
        time.sleep(2)

    except Exception as e:
        inserir_log(log_box, f"⚠️ Erro ao navegar: {e}")


# ===============================
# FUNÇÕES AUXILIARES
# ===============================


def verificar_botoes_step() -> int:
    """Verifica quantos botões de step estão disponíveis."""
    botoes_step = buscar_botao_por_texto("Take a step", todos=True)
    if isinstance(botoes_step, list):
        return len(botoes_step)
    if botoes_step is not None:
        return 1
    return 0


# ===============================
# FUNCÕES OTIMIZADAS ESPECÍFICAS
# ===============================


def buscar_botao_step_rapido() -> bool:
    """Busca específica ultra-rápida para botões Take a step."""
    driver = get_driver()
    if not driver:
        return False

    try:
        # XPath direto e mais específico
        xpath = "//button[contains(., 'Take a step')]"
        botoes = driver.find_elements(By.XPATH, xpath)

        # Verifica apenas o primeiro elemento encontrado
        if botoes:
            botao = botoes[0]
            return botao.is_displayed() and botao.is_enabled()

        # Fallback para links (raramente usado)
        xpath_link = "//a[contains(., 'Take a step')]"
        links = driver.find_elements(By.XPATH, xpath_link)
        if links:
            link = links[0]
            return link.is_displayed() and link.is_enabled()

        return False
    except Exception:
        return False


def clicar_step_rapido(log_box=None) -> bool:
    """Clica rapidamente no botão Take a step sem delays desnecessários - COM DEBUG E FALLBACKS."""
    driver = get_driver()
    if not driver:
        inserir_log(log_box, "❌ Driver não disponível (função rápida)", debug=True)
        return False

    try:
        inserir_log(log_box, "🔍 Buscando botões (função rápida)...", debug=True)

        # Lista de XPaths para tentar (do mais específico ao mais geral)
        xpath_variants = [
            "//button[contains(., 'Take a step')]",
            "//button[contains(text(), 'Take a step')]",
            "//button[text()='Take a step']",
            "//button[contains(., 'step')]",
            "//input[@type='submit'][contains(@value, 'Take a step')]",
            "//input[@type='button'][contains(@value, 'Take a step')]",
        ]

        botoes = []
        for xpath in xpath_variants:
            try:
                elementos = driver.find_elements(By.XPATH, xpath)
                if elementos:
                    botoes.extend(elementos)
                    inserir_log(
                        log_box,
                        f"📊 XPath '{xpath}' encontrou {len(elementos)} elementos",
                        debug=True,
                    )
            except Exception as e:
                inserir_log(log_box, f"❌ Erro no XPath '{xpath}': {e}", debug=True)

        inserir_log(
            log_box, f"📊 Total de elementos encontrados: {len(botoes)}", debug=True
        )

        if botoes:
            # Tenta o primeiro botão válido
            for i, botao in enumerate(botoes[:3]):  # Máximo 3 tentativas
                try:
                    is_displayed = botao.is_displayed()
                    is_enabled = botao.is_enabled()
                    text = (
                        botao.text.strip()
                        if hasattr(botao, "text")
                        else botao.get_attribute("value") or "N/A"
                    )

                    inserir_log(
                        log_box,
                        f"🔍 Botão {i + 1}: '{text}' (display: {is_displayed}, enabled: {is_enabled})",
                        debug=True,
                    )

                    if is_displayed and is_enabled:
                        # Delay mínimo apenas para parecer humano
                        delay = random.uniform(0.2, 0.5)
                        inserir_log(
                            log_box, f"⏰ Delay rápido: {delay:.2f}s", debug=True
                        )
                        time.sleep(delay)

                        botao.click()
                        registrar_acao("Passo")
                        inserir_log(log_box, "✔ Passo realizado (rápido)")
                        return True
                    else:
                        inserir_log(
                            log_box, f"❌ Botão {i + 1} não disponível", debug=True
                        )
                except Exception as e:
                    inserir_log(log_box, f"❌ Erro no botão {i + 1}: {e}", debug=True)

        # Fallback para links
        inserir_log(log_box, "🔍 Tentando links (função rápida)...", debug=True)
        xpath_link_variants = [
            "//a[contains(., 'Take a step')]",
            "//a[contains(text(), 'Take a step')]",
            "//a[text()='Take a step']",
            "//a[contains(., 'step')]",
        ]

        links = []
        for xpath in xpath_link_variants:
            try:
                elementos = driver.find_elements(By.XPATH, xpath)
                if elementos:
                    links.extend(elementos)
                    inserir_log(
                        log_box,
                        f"📊 XPath link '{xpath}' encontrou {len(elementos)} elementos",
                        debug=True,
                    )
            except Exception as e:
                inserir_log(
                    log_box, f"❌ Erro no XPath link '{xpath}': {e}", debug=True
                )

        inserir_log(log_box, f"📊 Total de links encontrados: {len(links)}", debug=True)

        if links:
            link = links[0]
            try:
                is_displayed = link.is_displayed()
                is_enabled = link.is_enabled()
                text = link.text.strip() if hasattr(link, "text") else "N/A"

                inserir_log(
                    log_box,
                    f"🔍 Link: '{text}' (display: {is_displayed}, enabled: {is_enabled})",
                    debug=True,
                )

                if is_displayed and is_enabled:
                    delay = random.uniform(0.2, 0.5)
                    time.sleep(delay)
                    link.click()
                    registrar_acao("Passo")
                    inserir_log(log_box, "✔ Passo realizado (rápido - link)")
                    return True
                else:
                    inserir_log(
                        log_box, "❌ Link não disponível (função rápida)", debug=True
                    )
            except Exception as e:
                inserir_log(log_box, f"❌ Erro no link: {e}", debug=True)

        inserir_log(
            log_box, "❌ Nenhum elemento válido encontrado (função rápida)", debug=True
        )
        return False
    except Exception as e:
        inserir_log(log_box, f"⚠️ Erro no step rápido: {e}")
        return False


# ===============================
# FUNÇÕES DE PASSO (STEP) - ORIGINAIS
# ===============================
