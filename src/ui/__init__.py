"""
SimpleMMO Bot - UI Module (Versão Simplificada)
Interface gráfica essencial do usuário e controladores básicos.

Módulos essenciais:
    gui: Interface principal simplificada
    base: Classes base e eventos essenciais
    components: Componentes básicos (Header, BotControl, Log)
    controller: Controle básico do bot (start/stop)
    data_manager: Gerenciamento simplificado de dados do player
"""

__version__ = "4.0.0"
__description__ = "Interface gráfica simplificada e controles essenciais"

from .gui import iniciar_interface

__all__ = ["iniciar_interface"]
