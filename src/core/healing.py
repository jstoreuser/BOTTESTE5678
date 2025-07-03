"""
Sistema de Cura SimpleMMO Bot

Este módulo contém funções relacionadas ao sistema de cura,
incluindo verificação de HP e execução de curas.
"""

import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from core.context import registrar_acao
from driver.manager import get_driver
from utils.logger import inserir_log
from utils.timing import sleep_interrompivel


def verificar_personagem_morto() -> bool:
    """Verifica se o personagem está morto."""
    driver = get_driver()
    if not driver:
        return False

    try:
        # Procura pelo link "How do I heal?" que indica personagem morto
        btn_heal = driver.find_element(
            By.XPATH, "//a[contains(text(), 'How do I heal?')]"
        )
        return btn_heal.is_displayed()
    except Exception:
        return False


def verificar_e_curar(log_box=None) -> bool:
    """Verifica se o personagem está morto e cura automaticamente."""
    from utils.notifier import notificar

    if not verificar_personagem_morto():
        return False

    # Personagem está morto, notifica e cura
    notificar(
        "Seu personagem morreu! O bot tentará curar automaticamente.",
        "Personagem Morto",
    )
    inserir_log(log_box, "💀 Personagem morto. Iniciando cura automática...", "error")

    return curar_personagem(log_box)


def curar_personagem(log_box=None) -> bool:
    """Cura o personagem morto."""
    driver = get_driver()
    if not driver:
        inserir_log(log_box, "❌ Driver não iniciado para curar personagem.")
        return False

    try:
        inserir_log(log_box, "💀 Personagem morto. Curando...")
        driver.get("https://web.simple-mmo.com/healer?new_page_refresh=true")
        time.sleep(3)

        botao = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(text(), 'Heal Character')]")
            )
        )
        botao.click()
        time.sleep(3)
        driver.get("https://web.simple-mmo.com/travel")
        time.sleep(3)

        inserir_log(log_box, "💊 Cura realizada.")
        return True

    except Exception as e:
        inserir_log(log_box, f"⚠️ Falha ao curar: {e}")
        return False


def verificar_e_curar_hp() -> bool:
    """Verifica HP e cura se necessário."""
    # Simplificado - sempre retorna True na versão sem monitoramento de HP
    return True


# Função original mantida para compatibilidade com o bot_loop atual
def curar(driver, log_fn=print) -> bool:
    """Função original mantida para compatibilidade."""
    try:
        log_fn("💀 Personagem morto. Curando...")
        driver.get("https://web.simple-mmo.com/healer?new_page_refresh=true")
        time.sleep(3)

        botao = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(text(), 'Heal Character')]")
            )
        )
        botao.click()
        time.sleep(3)
        driver.get("https://web.simple-mmo.com/travel")
        time.sleep(3)

        log_fn("💊 Cura realizada.")
        return True
    except Exception as e:
        log_fn(f"⚠️ Falha ao curar: {e}")
        return False
