import time

from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .manager import get_driver


def clicar_elemento(elemento: str | WebElement, tentativas: int = 3) -> bool:
    """Clica em um elemento - VERSÃO ULTRA-RÁPIDA."""
    driver = get_driver()
    if not driver:
        return False

    for tentativa in range(tentativas):
        try:
            if isinstance(elemento, str):
                # Timeout reduzido para 1 segundo
                elem = WebDriverWait(driver, 1).until(
                    EC.element_to_be_clickable((By.XPATH, elemento))
                )
            else:
                # WebElement - verificação mínima
                try:
                    _ = elemento.is_displayed()
                    elem = elemento
                except StaleElementReferenceException:
                    return False

            # Scroll suave para o elemento (apenas o necessário)
            driver.execute_script(
                "arguments[0].scrollIntoView({block: 'nearest', behavior: 'smooth'});",
                elem,
            )
            time.sleep(0.1)  # Espera mínima

            # Clicar
            elem.click()
            return True

        except StaleElementReferenceException:
            if tentativa < tentativas - 1:
                time.sleep(0.2)  # Espera reduzida
                continue
            return False
        except Exception:
            if tentativa < tentativas - 1:
                time.sleep(0.2)  # Espera reduzida
                continue
            return False

    return False


def buscar_botao_por_texto(
    texto: str, todos: bool = False
) -> list[WebElement] | WebElement | None:
    """Busca botão(ões) por texto - VERSÃO ULTRA-RÁPIDA."""
    driver = get_driver()
    if not driver:
        return None

    try:
        # Otimização especial para "Take a step" - XPath mais específico
        if "Take a step" in texto:
            # XPath otimizado para botões Take a step (mais comum)
            xpath_step = "//button[contains(., 'Take a step')]"
            elementos = driver.find_elements(By.XPATH, xpath_step)

            if not elementos:
                # Fallback para links (menos comum)
                xpath_step_link = "//a[contains(., 'Take a step')]"
                elementos = driver.find_elements(By.XPATH, xpath_step_link)
        else:
            # Lógica padrão para outros textos
            xpath_contem = f"//button[contains(text(), '{texto}')]"
            elementos = driver.find_elements(By.XPATH, xpath_contem)
            if not elementos:
                xpath_links = f"//a[contains(text(), '{texto}')]"
                elementos = driver.find_elements(By.XPATH, xpath_links)

        # Se não precisamos de todos, só verifica o primeiro
        if not todos and elementos:
            primeiro = elementos[0]
            try:
                if primeiro.is_displayed() and primeiro.is_enabled():
                    return primeiro
            except Exception:
                pass
            return None

        # Verificação rápida - apenas os primeiros 3 elementos para acelerar
        elementos_validos = []
        for el in elementos[:3]:
            try:
                if el.is_displayed() and el.is_enabled():
                    elementos_validos.append(el)
                    if not todos:  # Se não precisa de todos, para no primeiro
                        break
            except Exception:
                continue

        if elementos_validos:
            return elementos_validos if todos else elementos_validos[0]

        return None
    except Exception:
        return None


def fechar_interface_coleta() -> bool:
    """Fecha interfaces de coleta abertas."""
    driver = get_driver()
    if not driver:
        return False

    try:
        # Tenta fechar pelo X
        fechar_btn = driver.find_element(By.XPATH, "//button[@class='btn-close']")
        return clicar_elemento(fechar_btn)
    except Exception:
        try:
            # Tenta fechar por botões alternativos
            fechar_btn = driver.find_element(
                By.XPATH, "//button[contains(text(), 'Close')]"
            )
            return clicar_elemento(fechar_btn)
        except Exception:
            return False


def url_comeca_com(prefixo: str) -> bool:
    """Verifica se a URL atual começa com o prefixo especificado."""
    driver = get_driver()
    if not driver:
        return False

    try:
        return driver.current_url.startswith(prefixo)
    except Exception:
        return False


def janela_valida() -> bool:
    """Verifica se a janela do driver é válida."""
    driver = get_driver()
    if not driver:
        return False

    try:
        # Testa se a janela está aberta e acessível
        _ = driver.current_url
        return True
    except Exception:
        return False
