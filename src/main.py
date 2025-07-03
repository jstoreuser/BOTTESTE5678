"""
SimpleMMO Bot - Ponto de entrada principal (Versão Simplificada)

Este módulo fornece o ponto de entrada principal para o SimpleMMO Bot.
Inicializa a interface gráfica moderna e modular que permite controlar
as funcionalidades básicas do bot.

Modules:
    ui.gui: Interface gráfica modular e simplificada

Functions:
    main(): Função principal que inicia a interface

Usage:
    python main.py

Author: SimpleMMO Bot Team
Version: 4.0.0 - Arquitetura Completamente Simplificada (Core + Driver + UI)
"""

import os
import sys

# Add src directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.gui import iniciar_interface


def main() -> None:
    """Função principal para execução via CLI

    Inicia a interface gráfica do usuário que permite:
    - Configurar e controlar o bot
    - Visualizar logs
    - Gerenciar funções básicas (coleta e combate)

    Returns:
        None
    """
    iniciar_interface()


if __name__ == "__main__":
    main()
