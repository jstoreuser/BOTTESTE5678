"""
SimpleMMO Bot - Utils Module (Versão Simplificada)
Utilitários essenciais e funções auxiliares para o projeto.

Módulos essenciais:
    config: Carregamento de configurações (carregar_config)
    logger: Sistema de logging simplificado (inserir_log)
    timing: Controle de tempo e pausas (sleep_interrompivel, tempo_aleatorio)
    notifier: Notificações para o usuário (notificar)
"""

__version__ = "4.0.0"
__description__ = "Utilitários essenciais simplificados"

from .config import carregar_config, get_chromedriver_path, get_project_root
from .logger import inserir_log
from .notifier import notificar
from .timing import sleep_interrompivel, tempo_aleatorio

__all__ = [
    "carregar_config",
    "get_chromedriver_path", 
    "get_project_root",
    "inserir_log",
    "sleep_interrompivel",
    "tempo_aleatorio",
    "notificar",
]
