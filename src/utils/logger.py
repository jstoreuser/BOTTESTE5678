from datetime import datetime
import logging
import threading
import tkinter as tk

# Lista para armazenar logs recentes
logs_recentes: list[str] = []
ultima_msg_log: str | None = None
ultima_msg_tipo: str | None = None
ultima_msg_timestamp: str | None = None
lock_log = threading.Lock()

DEBUG_MODE = True


def inserir_log(
    box: tk.Text | None,
    msg: str,
    tipo: str = "info",
    forcar: bool = False,
    debug: bool = False,
) -> None:
    """Insere log na interface e no sistema de logging - VERSÃO SIMPLIFICADA."""
    global ultima_msg_log, ultima_msg_tipo, ultima_msg_timestamp

    # Timestamp atual
    timestamp_atual = datetime.now().strftime("%H:%M:%S")

    # Evita spam de mensagens idênticas EM POUCO TEMPO (dentro de 2 segundos)
    with lock_log:
        agora = datetime.now()
        se_ultimo_timestamp = ultima_msg_timestamp

        try:
            ultimo_tempo = datetime.strptime(
                se_ultimo_timestamp or "00:00:00", "%H:%M:%S"
            )
            ultimo_tempo = ultimo_tempo.replace(
                year=agora.year, month=agora.month, day=agora.day
            )
            tempo_diferenca = (agora - ultimo_tempo).total_seconds()
        except Exception:
            tempo_diferenca = 999  # Force update se houver erro

        # Só evita duplicação se for exatamente a mesma mensagem em menos de 2 segundos
        if (
            not forcar
            and ultima_msg_log == msg
            and ultima_msg_tipo == tipo
            and tempo_diferenca < 2.0
        ):
            return

        # Atualiza controle de spam
        ultima_msg_log = msg
        ultima_msg_tipo = tipo
        ultima_msg_timestamp = timestamp_atual

    # Formatação da mensagem
    if tipo == "error":
        emoji = "❌"
        prefix = "ERRO"
    elif tipo == "warning":
        emoji = "⚠️"
        prefix = "AVISO"
    elif tipo == "success":
        emoji = "✅"
        prefix = "OK"
    elif debug:
        emoji = "🔍"
        prefix = "DEBUG"
    else:
        emoji = "ℹ️"
        prefix = "INFO"

    msg_formatada = f"[{timestamp_atual}] {emoji} {prefix}: {msg}"

    # Log no sistema
    if tipo == "error":
        logging.error(msg)
    elif tipo == "warning":
        logging.warning(msg)
    else:
        logging.info(msg)

    # Adiciona ao histórico recente
    with lock_log:
        logs_recentes.append(msg_formatada)
        if len(logs_recentes) > 100:
            logs_recentes.pop(0)

    # Mostra na interface se disponível
    if box:
        try:
            # Insere no final
            box.insert(tk.END, msg_formatada + "\n")
            box.see(tk.END)

            # Limita o tamanho do log na interface
            lines = box.get(1.0, tk.END).split("\n")
            if len(lines) > 200:
                box.delete(1.0, f"{len(lines) - 150}.0")

        except tk.TclError:
            pass

        # Debug adicional
        if debug:
            logging.debug(msg_formatada)
