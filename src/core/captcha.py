import time

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from driver.manager import get_driver


def verificar_captcha() -> bool:
    """Verifica se há captcha na página."""
    driver = get_driver()
    if not driver:
        return False

    try:
        captcha = driver.find_element(
            By.XPATH, '//a[contains(text(), "I\'m a person!")]'
        )
        return captcha.is_displayed()
    except NoSuchElementException:
        return False
    except Exception:
        return False


def aguardar_resolucao(log_fn=print) -> None:
    """Aguarda a resolução do captcha pelo usuário."""
    from utils.notifier import notificar

    # Notifica o usuário
    notificar("CAPTCHA detectado! O bot está aguardando sua ação.", "CAPTCHA")

    log_fn("⚠️ CAPTCHA detectado. Aguardando resolução...")

    # Aguarda até o captcha ser resolvido
    while verificar_captcha():
        time.sleep(1)

    log_fn("✅ CAPTCHA resolvido.")
