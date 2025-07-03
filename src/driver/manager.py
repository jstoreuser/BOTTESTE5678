import logging
import os
import subprocess

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from utils.config import carregar_config

# Driver global
_driver: webdriver.Chrome | None = None


def get_driver() -> webdriver.Chrome | None:
    """Retorna a instância do driver."""
    global _driver

    if _driver:
        try:
            # Testa se o driver ainda está válido
            _ = _driver.current_url
            return _driver
        except Exception:
            logging.warning("Driver atual inválido, limpando referência")
            _driver = None

    return _driver


def iniciar_driver() -> webdriver.Chrome | None:
    """Inicia o driver do Chrome."""
    global _driver

    if _driver:
        try:
            # Testa se o driver ainda está válido
            _ = _driver.title
            return _driver
        except Exception:
            _driver = None

    # Primeiro, tentar conectar a um browser já existente
    driver_existente = conectar_ao_browser_existente()
    if driver_existente:
        return driver_existente

    try:
        config = carregar_config()
        chrome_options = Options()
        chrome_options.add_experimental_option(
            "debuggerAddress", config["remote_debugging_address"]
        )

        service = Service(config["chromedriver_path"])
        _driver = webdriver.Chrome(service=service, options=chrome_options)

        # Navegar para a URL inicial
        _driver.get(config["url"])

        logging.info("Driver iniciado com sucesso")
        return _driver

    except Exception as e:
        logging.error(f"Erro ao iniciar driver: {e}")
        _driver = None
        return None


def finalizar_driver() -> None:
    """Finaliza o driver do Chrome."""
    global _driver

    if _driver:
        try:
            _driver.quit()
            logging.info("Driver finalizado com sucesso")
        except Exception as e:
            logging.warning(f"Erro ao finalizar driver: {e}")
        finally:
            _driver = None


def conectar_ao_browser_existente() -> webdriver.Chrome | None:
    """Tenta conectar a um browser já aberto."""
    global _driver

    try:
        config = carregar_config()
        chrome_options = Options()
        chrome_options.add_experimental_option(
            "debuggerAddress", config["remote_debugging_address"]
        )

        service = Service(config["chromedriver_path"])
        _driver = webdriver.Chrome(service=service, options=chrome_options)

        # Testar se a conexão funciona
        _ = _driver.title

        logging.info("Conectado ao browser existente com sucesso")
        return _driver

    except Exception as e:
        logging.warning(f"Não foi possível conectar ao browser existente: {e}")
        _driver = None
        return None


def abrir_brave_browser() -> bool:
    """Abre o Brave browser com debugging habilitado usando o caminho e parâmetros específicos."""
    try:
        # Caminho fixo do Brave conforme especificado
        brave_path = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
        
        # Verificar se o arquivo existe
        if not os.path.exists(brave_path):
            logging.error(f"Brave browser não encontrado em: {brave_path}")
            return False

        # Comando para abrir o Brave com os parâmetros específicos
        comando = [
            brave_path,
            "--remote-debugging-port=9222",
            "--user-data-dir=C:\\temp\\brave_profile",
            "https://web.simple-mmo.com/travel"
        ]

        # Abrir o processo sem aguardar
        subprocess.Popen(comando, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Aguardar um momento para o browser inicializar
        import time

        time.sleep(3)
        logging.info("Brave browser iniciado com debugging habilitado")
        return True

    except Exception as e:
        logging.error(f"Erro ao abrir Brave browser: {e}")
        return False
