from core import bot_loop, context


def iniciar_bot(log_fn=print, config_bot=None):
    """Inicia o bot com configurações específicas."""
    if config_bot is None:
        config_bot = {
            "modo_attack_ativo": True,
            "modo_coleta_ativo": True,
        }

    # Usar as novas funções de estado
    context.definir_bot_rodando(True)

    try:
        bot_loop.bot_loop(log_fn, config_bot=config_bot)
    finally:
        # Garantir que o estado seja limpo quando o bot parar
        context.definir_bot_rodando(False)


def parar_bot():
    context.definir_bot_rodando(False)
    context.atualizar_configuracao("finalizar_bot", True)


def encerrar_bot():
    context.definir_bot_rodando(False)
    context.atualizar_configuracao("finalizar_bot", True)
