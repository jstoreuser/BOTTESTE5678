import random
import time

from core.context import encerrado, rodando


def tempo_aleatorio(
    base: float = 2.0, variacao: float = 1.0, chance_pausa: float = 0.1
) -> float:
    """Gera um tempo aleatório com base e variação."""
    tempo = base + random.uniform(-variacao, variacao)

    # Adiciona pausas aleatórias ocasionais
    if random.random() < chance_pausa:
        tempo += random.uniform(1.0, 3.0)

    return max(0.1, tempo)


def sleep_interrompivel(segundos: float) -> None:
    """Sleep que pode ser interrompido pela parada do bot."""
    inicio = time.time()

    while time.time() - inicio < segundos:
        if encerrado or not rodando:
            break
        time.sleep(0.1)
