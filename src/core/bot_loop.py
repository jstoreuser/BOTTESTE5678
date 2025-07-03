"""
SimpleMMO Bot - Loop Principal

Este módulo contém o loop principal do bot, responsável por coordenar
todas as atividades automatizadas.

Features:
- Sistema de batalha com fila de prioridades
- Coleta de recursos otimizada
"""

from collections.abc import Callable
import tkinter as tk
from typing import Any

from selenium.webdriver.common.by import By

from core import captcha, context, fight, gather, healing, step
from driver.actions import janela_valida, url_comeca_com
from driver.manager import finalizar_driver, get_driver, iniciar_driver
from utils.logger import inserir_log
from utils.timing import sleep_interrompivel, tempo_aleatorio


def bot_loop(
    log_fn: Callable[[str], None] = print,
    log_box: tk.Text | None = None,
    config_bot: dict[str, Any] | None = None,
):
    """Loop principal do bot - sistema unificado."""

    # Configuração inicial
    if config_bot is None:
        config_bot = {
            "modo_attack_ativo": True,
            "modo_coleta_ativo": True,
        }

    # Inicializa configurações
    for chave, valor in config_bot.items():
        context.atualizar_configuracao(chave, valor)

    inserir_log(log_box, "🚀 Bot loop iniciado (sistema unificado)", "info")

    driver = iniciar_driver()
    if not driver:
        log_fn("❌ Falha ao iniciar driver.")
        return

    # Sistema simplificado - sem fila de batalhas

    log_fn("✅ Bot iniciado.")

    # Loop principal
    erros_consecutivos = 0

    while True:
        # Verificar se a interface sinalizou o fim
        if context.obter_configuracao("finalizar_bot"):
            log_fn("👋 Bot finalizado.")
            break

        # Pausa para reduzir uso de CPU
        sleep_interrompivel(tempo_aleatorio(1.0, 0.5))

        # Verificar janela válida
        if not janela_valida():
            inserir_log(log_box, "⚠️ Conexão perdida, tentando reconectar...")
            # Limpar driver atual
            finalizar_driver()

            driver = iniciar_driver()
            if not driver:
                inserir_log(log_box, "❌ Falha ao reconectar driver")
                sleep_interrompivel(10)  # Aguardar mais tempo antes de tentar novamente
                continue
            sleep_interrompivel(3)
            continue

        try:
            # ========================================
            # RESOURCE MONITORING
            # ========================================
            # Verifica se o player tem recursos suficientes
            driver = get_driver()
            if driver:
                try:
                    # Verificamos se o player tem energia suficiente
                    try:
                        energy_element = driver.find_element(
                            By.CSS_SELECTOR, "span.energy-text"
                        )
                        current_energy = int(energy_element.text.strip())

                        # Verifica se deve pausar por falta de recursos
                        if current_energy <= 10:
                            inserir_log(log_box, "⏳ Aguardando energia...", debug=True)
                            sleep_interrompivel(tempo_aleatorio(10.0, 5.0))
                            continue
                    except Exception:
                        # Se não conseguir encontrar o elemento, continua normalmente
                        pass

                except Exception as e:
                    inserir_log(
                        log_box, f"⚠️ Erro ao verificar recursos: {e}", debug=True
                    )

            # Verificações críticas
            if captcha.verificar_captcha():
                captcha.aguardar_resolucao(log_fn)
                continue

            # Verificação de cura
            if not healing.verificar_e_curar_hp():
                # Sem HP suficiente e não conseguiu curar
                inserir_log(log_box, "⚠️ HP baixo, tentando curar...", "warning")
                sleep_interrompivel(tempo_aleatorio(10.0, 5.0))
                continue

            # Vamos verificar se estamos na URL do travel
            if not url_comeca_com("https://web.simple-mmo.com/travel"):
                # Se não estivermos na página correta, navegar para travel
                step.navegar_para_travel(log_box)
                continue

            # =========== FIGHT ==========
            modo_attack = context.obter_configuracao("modo_attack_ativo")
            if modo_attack:
                botao_attack = fight.localizar_botao_ataque()
                if botao_attack and fight.processar_ataque(botao_attack, log_box):
                    # Incrementar contador interno (não usando mais sistema de estatísticas)
                    sleep_interrompivel(tempo_aleatorio(2.0, 1.0))
                    continue

            # =========== GATHER ==========
            modo_coleta = context.obter_configuracao("modo_coleta_ativo")
            if modo_coleta and gather.processar_coleta(log_box):
                # Incrementar contador interno (não usando mais sistema de estatísticas)
                sleep_interrompivel(tempo_aleatorio(2.0, 1.0))
                continue

            # =========== STEPS ==========
            # Se não encontrou nada para fazer, dar um step
            if step.dar_step(log_box):
                # Incrementar contador interno (não usando mais sistema de estatísticas)
                sleep_interrompivel(tempo_aleatorio(1.0, 0.5))
                continue
            else:
                # Se falhou no step, aguardar um pouco
                sleep_interrompivel(tempo_aleatorio(3.0, 2.0))

            # Resetar contador de erros em caso de sucesso
            erros_consecutivos = 0

        except Exception as e:
            # Gerenciamento de erros
            erros_consecutivos += 1
            inserir_log(log_box, f"❌ Erro: {e}", "error")

            if erros_consecutivos >= 10:
                inserir_log(
                    log_box,
                    "⚠️ Muitos erros consecutivos, reiniciando driver...",
                    "error",
                )
                finalizar_driver()
                driver = iniciar_driver()
                erros_consecutivos = 0

            sleep_interrompivel(tempo_aleatorio(5.0, 3.0))

    # Cleanup
    finalizar_driver()


def executar_navegacao_otimizada(log_box, wave_ativo=False):
    """Executa a navegação otimizada na tela do travel.

    Args:
        log_box: Caixa de log
        wave_ativo: Parâmetro mantido para compatibilidade, não usado

    Returns:
        bool: True se encontrou e fez alguma ação, False caso contrário
    """
    # Procurar por botão de ataque
    botao_attack = fight.localizar_botao_ataque()
    if botao_attack and fight.processar_ataque(botao_attack, log_box):
        return True

    # Procurar por botão de coleta
    if gather.processar_coleta(log_box):
        return True

    # Se não encontrou nada, dar step
    return step.dar_step(log_box)


def iniciar_bot():
    """Função de inicialização do bot."""
    bot_loop()
