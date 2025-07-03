from tkinter.messagebox import showinfo


def notificar(msg: str, titulo: str = "Notificação") -> None:
    """Exibe uma notificação para o usuário."""
    try:
        showinfo(titulo, msg)
    except Exception:
        print(f"{titulo}: {msg}")
