"""
SimpleMMO Bot - Base Classes e Interfaces

Este módulo define as classes base e interfaces para o sistema modular do GUI.
Fornece a base para expansão futura e modularidade.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
import threading
import time
from typing import Any, Dict, List, Optional, Protocol


class EventType(Enum):
    """Tipos de eventos do sistema"""

    PLAYER_DATA_UPDATED = "player_data_updated"
    BOT_STATUS_CHANGED = "bot_status_changed"
    LOG_MESSAGE = "log_message"
    CONFIG_CHANGED = "config_changed"
    ERROR_OCCURRED = "error_occurred"
    STATS_UPDATED = "stats_updated"


@dataclass
class Event:
    """Evento do sistema"""

    type: EventType
    data: Dict[str, Any]
    timestamp: Optional[float] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()


class EventSubscriber(Protocol):
    """Interface para assinantes de eventos"""

    def handle_event(self, event: Event) -> None:
        """Manipula um evento"""
        ...


class EventManager:
    """Gerenciador central de eventos"""

    def __init__(self):
        self._subscribers: Dict[EventType, List[EventSubscriber]] = {}
        self._lock = threading.Lock()

    def subscribe(self, event_type: EventType, subscriber: EventSubscriber) -> None:
        """Inscreve um assinante para um tipo de evento"""
        with self._lock:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            self._subscribers[event_type].append(subscriber)

    def unsubscribe(self, event_type: EventType, subscriber: EventSubscriber) -> None:
        """Remove inscrição de um assinante"""
        with self._lock:
            if event_type in self._subscribers:
                try:
                    self._subscribers[event_type].remove(subscriber)
                except ValueError:
                    pass

    def publish(self, event: Event) -> None:
        """Publica um evento para todos os assinantes"""
        # print(f"DEBUG: EventManager publicando evento: {event.type}, data: {event.data}")

        with self._lock:
            subscribers = self._subscribers.get(event.type, []).copy()

        # print(f"DEBUG: {len(subscribers)} subscribers para {event.type}")

        for subscriber in subscribers:
            try:
                # print(f"DEBUG: Enviando evento para {type(subscriber).__name__}")
                subscriber.handle_event(event)
            except Exception as e:
                print(
                    f"ERROR: Erro ao processar evento {event.type} em {type(subscriber).__name__}: {e}"
                )


@dataclass
class PlayerData:
    """Dados do player estruturados"""

    # Stats vitais
    health: int = 0
    max_health: int = 0
    energy: int = 0
    max_energy: int = 0
    quest_points: int = 0
    max_quest_points: int = 0

    # Recursos
    gold: int = 0
    bank: int = 0
    diamonds: int = 0

    # Progresso
    level: int = 0
    exp_remaining: int = 0
    steps: int = 0

    # Status
    status: str = "unknown"
    error_message: Optional[str] = None
    last_updated: Optional[float] = None

    def __post_init__(self):
        if self.last_updated is None:
            self.last_updated = time.time()

    @property
    def health_percentage(self) -> float:
        """Percentual de HP"""
        if self.max_health <= 0:
            return 0
        return (self.health / self.max_health) * 100

    @property
    def energy_percentage(self) -> float:
        """Percentual de energia"""
        if self.max_energy <= 0:
            return 0
        return (self.energy / self.max_energy) * 100

    @property
    def quest_percentage(self) -> float:
        """Percentual de quest points"""
        if self.max_quest_points <= 0:
            return 0
        return (self.quest_points / self.max_quest_points) * 100

    @property
    def needs_healing(self) -> bool:
        """Verifica se precisa de cura"""
        return self.health_percentage < 80

    @property
    def low_energy(self) -> bool:
        """Verifica se tem energia baixa"""
        return self.energy < 3

    @property
    def can_quest(self) -> bool:
        """Verifica se pode fazer quests"""
        return self.quest_points > 0


@dataclass
class BotConfiguration:
    """Configuração do bot"""

    # Modos de operação
    attack_mode: bool = True
    gather_mode: bool = True

    # Configurações de timing
    update_interval: int = 8
    stats_interval: int = 10
    cache_duration: int = 5

    # Configurações de healing
    healing_threshold: int = 80

    # Configurações de energia
    energy_threshold: int = 3

    # Browser settings
    browser_type: str = "brave"  # brave, chrome
    debug_port: int = 9222

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            "modo_attack_ativo": self.attack_mode,
            "modo_coleta_ativo": self.gather_mode,
        }


class UIComponent(ABC):
    """Classe base para componentes da UI"""

    def __init__(self, parent, event_manager: EventManager):
        self.parent = parent
        self.event_manager = event_manager
        self._setup_ui()
        self._setup_events()

    @abstractmethod
    def _setup_ui(self) -> None:
        """Configura a interface do componente"""
        pass

    @abstractmethod
    def _setup_events(self) -> None:
        """Configura eventos do componente"""
        pass

    def publish_event(self, event_type: EventType, data: Dict[str, Any]) -> None:
        """Publica um evento"""
        event = Event(type=event_type, data=data)
        self.event_manager.publish(event)


class DataProvider(ABC):
    """Interface para provedores de dados"""

    @abstractmethod
    def get_data(self) -> Any:
        """Obtém dados"""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Verifica se os dados estão disponíveis"""
        pass


class LogLevel(Enum):
    """Níveis de log com cores e prioridades"""

    # Logs do sistema (alta prioridade)
    SISTEMA = ("SISTEMA", "🔧", "#2E86DE")  # Azul
    BOT = ("BOT", "🤖", "#10AC84")  # Verde

    # Logs de dados (prioridade média)
    DADOS = ("DADOS", "📊", "#F79F1F")  # Laranja
    INFO = ("INFO", "ℹ️", "#3742FA")  # Azul claro

    # Logs de problemas (alta prioridade)
    ERROR = ("ERROR", "❌", "#FF3838")  # Vermelho
    WARNING = ("WARNING", "⚠️", "#FFA502")  # Amarelo

    # Debug (baixa prioridade)
    DEBUG = ("DEBUG", "🔍", "#A4B0BE")  # Cinza

    def __init__(self, display_name: str, icon: str, color: str):
        self.display_name = display_name
        self.icon = icon
        self.color = color

    @property
    def priority(self) -> int:
        """Prioridade do log (menor número = maior prioridade)"""
        priorities = {
            "ERROR": 1,
            "SISTEMA": 2,
            "BOT": 3,
            "WARNING": 4,
            "DADOS": 5,
            "INFO": 6,
            "DEBUG": 7,
        }
        return priorities.get(self.display_name, 6)


@dataclass
class LogEntry:
    """Entrada de log aprimorada"""

    level: LogLevel
    message: str
    timestamp: Optional[float] = None
    component: Optional[str] = None
    count: int = 1  # Para agrupar mensagens repetidas

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()
        # Garantir que timestamp é sempre um float válido
        if not isinstance(self.timestamp, (int, float)):
            self.timestamp = time.time()

    def format(self, show_icons: bool = True, compact: bool = False) -> str:
        """Formata a entrada de log com opções de estilo"""
        time_str = time.strftime("%H:%M:%S", time.localtime(self.timestamp))

        # Formato compacto ou completo
        if compact:
            if show_icons:
                return f"{time_str} {self.level.icon} {self.message}"
            else:
                return f"{time_str} [{self.level.display_name}] {self.message}"

        # Formato completo
        icon = self.level.icon if show_icons else ""
        component_str = f"[{self.component}]" if self.component else ""
        count_str = f" (x{self.count})" if self.count > 1 else ""

        return f"[{time_str}] {icon}[{self.level.display_name}] {component_str} {self.message}{count_str}"

    def format_colored(self) -> str:
        """Formata com cores para terminais que suportam"""
        time_str = time.strftime("%H:%M:%S", time.localtime(self.timestamp))
        component_str = f"[{self.component}]" if self.component else ""
        count_str = f" (x{self.count})" if self.count > 1 else ""

        return f"[{time_str}] {self.level.icon}[{self.level.display_name}] {component_str} {self.message}{count_str}"

    def __eq__(self, other) -> bool:
        """Compara mensagens para detectar repetições"""
        if not isinstance(other, LogEntry):
            return False
        return (
            self.level == other.level
            and self.message == other.message
            and self.component == other.component
        )
