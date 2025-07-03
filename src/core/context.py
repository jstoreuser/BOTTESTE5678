import threading

# Estados globais do bot
rodando = False
encerrado = False
aguardando_step = False
thread_bot_iniciada = False

# Configurações dinâmicas do bot (atualizáveis em tempo real)
configuracoes_bot = {
    "modo_attack_ativo": True,
    "modo_coleta_ativo": True,
    "finalizar_bot": False,
}

# Contadores e controles
cliques = 0
_em_get_user_gold = False

# Threading
lock = threading.Lock()

# Histórico e logs
historico_acoes: list[tuple[str, str]] = []
ultima_excecao: str | None = None


def registrar_acao(acao: str) -> None:
    """Registra uma ação no histórico e notifica callbacks."""
    from datetime import datetime

    timestamp = datetime.now().strftime("%H:%M:%S")
    with lock:
        historico_acoes.append((timestamp, acao))
        if len(historico_acoes) > 50:
            historico_acoes.pop(0)

    # Notificar callbacks sobre a ação executada
    notificar_acao_executada(acao)


def get_historico_acoes() -> list[tuple[str, str]]:
    """Retorna uma cópia do histórico de ações."""
    with lock:
        return historico_acoes.copy()


def incrementar_cliques() -> None:
    """Incrementa o contador de cliques."""
    global cliques
    with lock:
        cliques += 1


def atualizar_configuracao(chave: str, valor: bool) -> None:
    """Atualiza uma configuração do bot em tempo real."""
    with lock:
        configuracoes_bot[chave] = valor


def obter_configuracao(chave: str) -> bool:
    """Obtém uma configuração do bot de forma thread-safe."""
    with lock:
        return configuracoes_bot.get(chave, True)


def obter_todas_configuracoes() -> dict:
    """Obtém todas as configurações de forma thread-safe."""
    with lock:
        return configuracoes_bot.copy()


def set_em_get_user_gold(valor: bool) -> None:
    """Define o estado de obtenção de ouro do usuário."""
    global _em_get_user_gold
    with lock:
        _em_get_user_gold = valor


def get_em_get_user_gold() -> bool:
    """Retorna se está obtendo ouro do usuário."""
    with lock:
        return _em_get_user_gold


# Callbacks para notificar sobre atualizações de dados
_callbacks_atualizacao_dados = []


def registrar_callback_atualizacao_dados(callback) -> None:
    """Registra um callback para ser chamado após ações do bot"""
    with lock:
        if callback not in _callbacks_atualizacao_dados:
            _callbacks_atualizacao_dados.append(callback)


def remover_callback_atualizacao_dados(callback) -> None:
    """Remove um callback do sistema"""
    with lock:
        if callback in _callbacks_atualizacao_dados:
            _callbacks_atualizacao_dados.remove(callback)


def notificar_acao_executada(nome_acao: str) -> None:
    """Notifica todos os callbacks que uma ação foi executada"""
    with lock:
        callbacks = _callbacks_atualizacao_dados.copy()

    for callback in callbacks:
        try:
            callback(nome_acao)
        except Exception:
            # Silenciosamente ignora erros nos callbacks
            pass


def definir_bot_rodando(estado: bool) -> None:
    """Define se o bot está rodando."""
    global rodando
    with lock:
        rodando = estado


def obter_bot_rodando() -> bool:
    """Retorna se o bot está rodando."""
    with lock:
        return rodando
