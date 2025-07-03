"""
Sistema de Batalha SimpleMMO Bot

Este módulo contém funções relacionadas ao sistema de batalha,
incluindo detecção de inimigos, processamento de ataques e
gerenciamento da fila de batalha.
"""

import logging
import random
import time

from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from core.context import registrar_acao
from driver.actions import clicar_elemento, url_comeca_com
from driver.manager import get_driver
from utils.logger import inserir_log
from utils.timing import sleep_interrompivel


def atacar(driver, log_fn=print) -> bool:
    """Função original mantida para compatibilidade."""
    try:
        wait = WebDriverWait(driver, 15)
        wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[text()='Attack' and not(@disabled)]")
            )
        )
        while True:
            botoes = driver.find_elements(
                By.XPATH, "//button[text()='Attack' and not(@disabled)]"
            )
            if not botoes:
                break
            botao = botoes[0]
            if botao.is_displayed() and botao.is_enabled():
                botao.click()
                registrar_acao("Ataque")
                log_fn("⚔️ Ataque realizado")
                time.sleep(random.uniform(3.0, 5.0))
            else:
                break
        try:
            btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(text(), 'Leave')]")
                )
            )
            btn.click()
            log_fn("🚪 Saiu da luta")
            time.sleep(2)
            return True
        except Exception:
            return False
    except Exception:
        logging.exception("Erro em atacar:")
        return False


def verificar_captcha_combate() -> bool:
    """Verifica se há captcha na interface de combate."""
    driver = get_driver()
    if not driver:
        return False

    try:
        captcha = driver.find_element(
            By.XPATH,
            "//a[@href='/i-am-not-a-bot' and contains(text(), 'Press here to verify')]",
        )
        return captcha.is_displayed()
    except NoSuchElementException:
        return False
    except Exception:
        return False


def aguardar_captcha_combate(log_box=None) -> None:
    """Aguarda resolução do captcha no combate."""
    from utils.notifier import notificar

    notificar(
        "CAPTCHA detectado no combate! O bot está aguardando sua ação.", "CAPTCHA"
    )
    inserir_log(log_box, "⚠️ CAPTCHA no combate detectado. Aguardando resolução...")

    # Aguarda até o captcha ser resolvido
    while verificar_captcha_combate():
        sleep_interrompivel(1)

    inserir_log(log_box, "✅ CAPTCHA do combate resolvido.")


def atacar_inimigo(log_box=None) -> bool:
    """Versão modular para atacar inimigos - CONTAGEM CORRETA."""
    driver = get_driver()
    if not driver:
        inserir_log(log_box, "❌ Driver não iniciado para atacar inimigo.")
        return False

    try:
        ataques_realizados = 0
        max_ataques = 100
        timeout_sem_botao = 0
        max_timeout_sem_botao = 8

        inserir_log(log_box, "⚔️ Iniciando sequência de ataques...", forcar=True)

        while (
            ataques_realizados < max_ataques
            and timeout_sem_botao < max_timeout_sem_botao
        ):
            try:
                # VERIFICA CAPTCHA PRIMEIRO
                if verificar_captcha_combate():
                    aguardar_captcha_combate(log_box)
                    continue

                # Verifica se ainda está na interface de combate
                if not url_comeca_com("https://web.simple-mmo.com/npcs/attack/"):
                    inserir_log(
                        log_box, "🔄 Saiu da interface de combate automaticamente"
                    )
                    # RETORNA TRUE INDICANDO QUE O COMBATE FOI CONCLUÍDO
                    return True

                # Verifica se há botão Leave disponível ANTES de tentar atacar
                try:
                    leave_btn = driver.find_element(
                        By.XPATH, "//button[contains(text(), 'Leave')]"
                    )
                    if leave_btn.is_displayed() and leave_btn.is_enabled():
                        inserir_log(log_box, "🏁 Combate finalizado, saindo...")
                        leave_btn.click()
                        sleep_interrompivel(2)
                        # RETORNA TRUE INDICANDO QUE VENCEU O COMBATE
                        return True
                except NoSuchElementException:
                    pass

                # Aguarda explicitamente o botão de ataque ficar clicável
                try:
                    botao_ataque = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable(
                            (
                                By.XPATH,
                                "//button[normalize-space(text())='Attack' and not(@disabled)]",
                            )
                        )
                    )

                    timeout_sem_botao = 0
                    botao_ataque.click()
                    ataques_realizados += 1
                    inserir_log(log_box, f"⚔️ Ataque {ataques_realizados} executado")
                    registrar_acao("Ataque")

                    tempo_espera = random.uniform(1.0, 1.8)
                    sleep_interrompivel(tempo_espera)

                except TimeoutException:
                    timeout_sem_botao += 1
                    inserir_log(
                        log_box,
                        f"⏰ Timeout aguardando botão ({timeout_sem_botao}/{max_timeout_sem_botao})",
                    )

                    if not url_comeca_com("https://web.simple-mmo.com/npcs/attack/"):
                        inserir_log(
                            log_box, "🔄 Saiu da interface de combate (timeout)"
                        )
                        return True

                    sleep_interrompivel(0.5)
                    continue

            except StaleElementReferenceException:
                inserir_log(log_box, "🔄 Elemento obsoleto, recarregando...")
                sleep_interrompivel(0.5)
                continue
            except Exception as e:
                inserir_log(log_box, f"⚠️ Erro durante ataque: {e}")
                break

        # Tenta sair da luta
        try:
            leave_btn = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(text(), 'Leave')]")
                )
            )
            leave_btn.click()
            inserir_log(log_box, f"🚪 Saiu da luta após {ataques_realizados} ataques")
            sleep_interrompivel(1.5)
            # RETORNA TRUE APENAS SE CONSEGUIU SAIR NORMALMENTE (VITÓRIA)
            return True
        except TimeoutException:
            inserir_log(log_box, "🔄 Forçando navegação para travel...")
            try:
                driver.get("https://web.simple-mmo.com/travel")
                sleep_interrompivel(2)
                inserir_log(log_box, "✅ Retornou à página de travel")
                # RETORNA FALSE POIS TEVE QUE FORÇAR SAÍDA (POSSIVELMENTE PERDEU)
                return False
            except Exception as e:
                inserir_log(log_box, f"❌ Erro ao forçar navegação: {e}")
                return False
        except Exception as e:
            inserir_log(log_box, f"⚠️ Erro ao sair da luta: {e}")
            return False

    except Exception as e:
        inserir_log(log_box, f"❌ Erro geral no combate: {e}", "error")
        return False


def verificar_attack_disponivel_pagina_principal():
    """Verifica se há botão de ataque disponível na página principal."""
    driver = get_driver()
    if not driver:
        return None

    try:
        # Busca tanto <a> quanto <button> com texto 'Attack'
        elementos = driver.find_elements(
            By.XPATH,
            "//a[contains(text(), 'Attack')] | //button[contains(text(), 'Attack')]",
        )
        for el in elementos:
            if el.is_displayed() and el.is_enabled():
                return el
        return None
    except Exception:
        return None


def processar_ataque(botao_attack, log_box=None) -> bool:
    """Processa um ataque clicando no botão e aguardando a interface."""
    driver = get_driver()
    if not driver:
        return False

    try:
        inserir_log(log_box, "🎯 Iniciando ataque em NPC...")
        sucesso = clicar_elemento(botao_attack)

        if not sucesso:
            inserir_log(log_box, "❌ Falha ao clicar no botão Attack")
            return False

        # Aguarda até entrar na interface de luta (timeout 10s)
        inserir_log(log_box, "⏳ Aguardando carregar interface de combate...")

        entrou_em_combate = False
        for _ in range(20):  # 20 tentativas de 0.5s = 10s total
            if url_comeca_com("https://web.simple-mmo.com/npcs/attack/"):
                entrou_em_combate = True
                break
            sleep_interrompivel(0.5)

        if entrou_em_combate:
            inserir_log(log_box, "✅ Interface de combate carregada")
            return atacar_inimigo(log_box)
        inserir_log(log_box, "❌ Timeout: Interface de combate não carregou")
        return False

    except Exception as e:
        inserir_log(log_box, f"❌ Erro ao processar ataque: {e}", "error")
        return False


def localizar_botao_ataque():
    """
    Localiza o botão de ataque na página atual.

    Returns:
        O elemento do botão de ataque se encontrado, None caso contrário
    """
    return verificar_attack_disponivel_pagina_principal()


# ========================================
# BATTLE QUEUE INTEGRATION (Inspirado no JavaScript Bot)
# ========================================


def queue_fight_from_travel(enemy_name: str, url: str, log_box=None) -> bool:
    """
    Executa batalha encontrada durante travel diretamente (sem fila)

    Args:
        enemy_name: Nome do inimigo
        url: URL da batalha
        log_box: Widget de log

    Returns:
        True se executou a batalha
    """
    try:
        inserir_log(log_box, f"⚔️ Iniciando batalha: {enemy_name}")

        # Navegar para a URL da batalha
        driver = get_driver()
        if not driver:
            inserir_log(log_box, "❌ Driver não disponível para batalha", "error")
            return False

        driver.get(url)
        sleep_interrompivel(2.0)

        # Executar batalha
        return atacar_inimigo(log_box)

    except Exception as e:
        inserir_log(log_box, f"❌ Erro na batalha: {e}", "error")
        return False


def queue_arena_fight(enemy_name: str, url: str, log_box=None) -> bool:
    """
    Executa batalha de arena diretamente (sem fila)

    Args:
        enemy_name: Nome do inimigo
        url: URL da batalha
        log_box: Widget de log

    Returns:
        True se executou a batalha
    """
    try:
        inserir_log(log_box, f"⚔️ Iniciando batalha de arena: {enemy_name}")

        # Navegar para a URL da batalha
        driver = get_driver()
        if not driver:
            inserir_log(log_box, "❌ Driver não disponível para batalha", "error")
            return False

        driver.get(url)
        sleep_interrompivel(2.0)

        # Executar batalha
        return atacar_inimigo(log_box)

    except Exception as e:
        inserir_log(log_box, f"❌ Erro na batalha de arena: {e}", "error")
        return False


def process_queued_fight(log_box=None) -> bool:
    """
    Função mantida para compatibilidade - agora apenas processa ataques diretos

    Returns:
        True se processou um ataque
    """
    try:
        # Verificar se há botão de attack disponível na página atual
        botao_attack = verificar_attack_disponivel_pagina_principal()
        if botao_attack:
            return processar_ataque(botao_attack, log_box)
        return False

    except Exception as e:
        inserir_log(log_box, f"❌ Erro ao processar ataque: {e}", "error")
        return False


def has_queued_fights() -> bool:
    """Função mantida para compatibilidade - sempre retorna False (sem fila)"""
    return False


def get_battle_queue_status() -> str:
    """Função mantida para compatibilidade - sem fila"""
    return "Sistema de fila removido - batalhas executadas diretamente"
