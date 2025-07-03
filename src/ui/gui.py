"""
SimpleMMO Bot - Interface Gráfica Principal (Simplificada)

Interface moderna e modular para o SimpleMMO Bot.
Utiliza sistema de eventos para comunicação entre componentes.

Features:
- Arquitetura modular e expansível
- Sistema de eventos centralizado
- Threading otimizado
- Interface responsiva
- Logs avançados
- Configuração flexível

Author: SimpleMMO Bot Team
Version: 3.1.0 - Simplificado
"""

import threading
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any, Dict

from .base import Event, EventManager, EventType, LogEntry, LogLevel
from .components import (
    BotControlComponent,
    HeaderComponent,
    LogComponent,
)
from .data_manager import PlayerDataExtractor


class ModernBotGUI:
    """Interface principal moderna do SimpleMMO Bot"""

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.event_manager = EventManager()
        self.data_manager = PlayerDataExtractor(self.event_manager)
        self.components: Dict[str, Any] = {}

        self._setup_window()
        self._setup_components()
        self._setup_event_handlers()
        self._start_systems()

    def _setup_window(self) -> None:
        """Configura janela principal"""
        self.root.title("SimpleMMO Bot v3.0 - Modular")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)

        # Configurar tema
        style = ttk.Style()
        if "clam" in style.theme_names():
            style.theme_use("clam")

        # Cores e estilo
        self.root.configure(bg="#f5f5f5")

        # Protocolo de fechamento
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _setup_components(self) -> None:
        """Configura todos os componentes da interface"""

        # Header
        self.components["header"] = HeaderComponent(self.root, self.event_manager)

        # Notebook para abas
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # === ABA PRINCIPAL ===
        main_tab = ttk.Frame(self.notebook)
        self.notebook.add(main_tab, text="🏠 Principal")

        # Layout da aba principal
        left_frame = ttk.Frame(main_tab)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        right_frame = ttk.Frame(main_tab)
        right_frame.pack(side="right", fill="y", padx=(5, 0))

        # Componentes da aba principal

        self.components["bot_control"] = BotControlComponent(
            right_frame, self.event_manager
        )
        self.components["bot_control"].frame.pack(fill="x")

        # === ABA DE LOGS ===
        logs_tab = ttk.Frame(self.notebook)
        self.notebook.add(logs_tab, text="📋 Logs")

        self.components["logs"] = LogComponent(logs_tab, self.event_manager)
        self.components["logs"].frame.pack(fill="both", expand=True)

        # === ABA DE CONFIGURAÇÕES ===
        config_tab = ttk.Frame(self.notebook)
        self.notebook.add(config_tab, text="⚙️ Configurações")

        # Placeholder para configurações futuras
        ttk.Label(
            config_tab,
            text="🚧 Configurações avançadas em desenvolvimento...",
            font=("Arial", 12),
        ).pack(expand=True)

    def _setup_event_handlers(self) -> None:
        """Configura manipuladores de eventos personalizados"""

        # Handler para mudanças de status do bot
        self.event_manager.subscribe(EventType.BOT_STATUS_CHANGED, self)

        # Handler para mudanças de configuração
        self.event_manager.subscribe(EventType.CONFIG_CHANGED, self)

        # Handler para logs do sistema
        self.event_manager.subscribe(EventType.LOG_MESSAGE, self)

    def handle_event(self, event: Event) -> None:
        """Manipula eventos do sistema"""
        if event.type == EventType.BOT_STATUS_CHANGED:
            self._handle_bot_status_change(event)
        elif event.type == EventType.CONFIG_CHANGED:
            self._handle_config_change(event)

    def _handle_bot_status_change(self, event: Event) -> None:
        """Manipula mudanças de status do bot"""
        status = event.data.get("status")

        if status == "starting":
            self._start_bot_worker(event.data.get("config"))
        elif status == "stopping":
            self._stop_bot_worker()

    def _handle_config_change(self, event: Event) -> None:
        """Manipula mudanças de configuração"""
        action = event.data.get("action")

        if action == "force_player_update":
            self.data_manager.force_update()
        elif action == "update_bot_config":
            # Atualizar configuração do bot com novas opções
            # As opções de quest_mode e player_stats_mode foram removidas
            pass

    def _start_bot_worker(self, config: Any) -> None:
        """Inicia worker do bot em thread separada"""

        def bot_worker():
            try:
                # Log de início
                log_entry = LogEntry(
                    LogLevel.BOT,
                    "Bot iniciado com configurações ativas",
                    component="BotManager",
                )
                self.event_manager.publish(
                    Event(EventType.LOG_MESSAGE, {"entry": log_entry})
                )

                # Importar e iniciar o controlador do bot
                from ui import controller

                controller.iniciar_bot(
                    self._log_from_bot,
                    config.__dict__ if hasattr(config, "__dict__") else config,
                )

                # Publicar status de sucesso
                self.event_manager.publish(
                    Event(EventType.BOT_STATUS_CHANGED, {"status": "running"})
                )

            except Exception as e:
                # Log de erro
                log_entry = LogEntry(
                    LogLevel.ERROR, f"Erro ao iniciar bot: {e}", component="BotManager"
                )
                self.event_manager.publish(
                    Event(EventType.LOG_MESSAGE, {"entry": log_entry})
                )

                # Publicar status de erro
                self.event_manager.publish(
                    Event(EventType.BOT_STATUS_CHANGED, {"status": "error"})
                )

                # Resetar botões na UI
                self.root.after(0, self._reset_bot_ui)

        threading.Thread(target=bot_worker, daemon=True).start()

    def _stop_bot_worker(self) -> None:
        """Para o bot"""
        try:
            print("DEBUG: _stop_bot_worker chamado")
            from core import context
            from ui import controller

            # Log de início da parada
            log_entry = LogEntry(
                LogLevel.BOT, "Iniciando parada do bot...", component="BotManager"
            )
            self.event_manager.publish(
                Event(EventType.LOG_MESSAGE, {"entry": log_entry})
            )

            # Parar o bot
            controller.parar_bot()
            print(f"DEBUG: context.rodando após parar_bot: {context.rodando}")

            # Aguardar um momento para garantir que o bot parou
            import time

            time.sleep(0.5)

            # Log de parada concluída
            log_entry = LogEntry(
                LogLevel.BOT, "Bot parado pelo usuário", component="BotManager"
            )
            self.event_manager.publish(
                Event(EventType.LOG_MESSAGE, {"entry": log_entry})
            )

            # Publicar status de parada
            self.event_manager.publish(
                Event(EventType.BOT_STATUS_CHANGED, {"status": "stopped"})
            )
            print("DEBUG: Evento BOT_STATUS_CHANGED (stopped) publicado")

            # Forçar atualização da UI na thread principal
            self.root.after(100, self._force_ui_update)

        except Exception as e:
            print(f"DEBUG: Erro em _stop_bot_worker: {e}")
            log_entry = LogEntry(
                LogLevel.ERROR, f"Erro ao parar bot: {e}", component="BotManager"
            )
            self.event_manager.publish(
                Event(EventType.LOG_MESSAGE, {"entry": log_entry})
            )

    def _force_ui_update(self) -> None:
        """Força atualização da UI"""
        print("DEBUG: _force_ui_update chamado")
        # CORREÇÃO: Não publicar evento novamente para evitar recursão
        # Em vez disso, atualizar componentes diretamente
        if "bot_control" in self.components:
            bot_control = self.components["bot_control"]
            if bot_control.bot_running:
                bot_control.bot_running = False
                bot_control.start_btn.config(state="normal")
                bot_control.stop_btn.config(state="disabled")
                bot_control.bot_status_var.set("⏸️ Bot Parado")

    def _log_from_bot(self, message: str, level: str = "INFO"):
        """Callback para logs vindos do bot"""
        # Converter string para LogLevel enum
        level_mapping = {
            "DEBUG": LogLevel.DEBUG,
            "INFO": LogLevel.INFO,
            "WARNING": LogLevel.WARNING,
            "ERROR": LogLevel.ERROR,
            "BOT": LogLevel.BOT,
            "SISTEMA": LogLevel.SISTEMA,
            "DADOS": LogLevel.DADOS,
        }
        log_level = level_mapping.get(level.upper(), LogLevel.INFO)
        log_entry = LogEntry(log_level, message, component="Bot")
        self.event_manager.publish(Event(EventType.LOG_MESSAGE, {"entry": log_entry}))

    def _reset_bot_ui(self) -> None:
        """Reseta interface do bot após erro"""
        if "bot_control" in self.components:
            self.components["bot_control"].bot_running = False
            self.components["bot_control"].start_btn.config(state="normal")
            self.components["bot_control"].stop_btn.config(state="disabled")

    def _start_systems(self) -> None:
        """Inicia sistemas de background"""
        # Log inicial
        log_entry = LogEntry(
            LogLevel.SISTEMA, "Interface moderna iniciada com sucesso!", component="GUI"
        )
        self.event_manager.publish(Event(EventType.LOG_MESSAGE, {"entry": log_entry}))

        log_entry = LogEntry(
            LogLevel.INFO, "Versão: SimpleMMO Bot v3.0 - Modular", component="GUI"
        )
        self.event_manager.publish(Event(EventType.LOG_MESSAGE, {"entry": log_entry}))

        log_entry = LogEntry(LogLevel.INFO, "Sistema de eventos ativo", component="GUI")
        self.event_manager.publish(Event(EventType.LOG_MESSAGE, {"entry": log_entry}))

        # Iniciar atualização periódica de dados do player
        self.root.after(3000, self._start_data_updates)

    def _start_data_updates(self) -> None:
        """Inicia atualizações inteligentes de dados"""
        # Primeira verificação de dados (sem forçar)
        current_data = self.data_manager.get_data()

        if current_data is None:
            # Só força update inicial se não há dados E se popup estiver disponível
            self.data_manager.force_update()

        self.event_manager.publish(
            Event(
                EventType.LOG_MESSAGE,
                {
                    "entry": LogEntry(
                        LogLevel.INFO,
                        "Sistema de atualização inteligente de dados iniciado",
                        component="DataManager",
                    )
                },
            )
        )

        # Configurar verificações periódicas (menos frequentes)
        self._schedule_next_check()

    def _schedule_next_check(self) -> None:
        """Agenda próxima verificação de dados (não update forçado)"""

        def check_and_update():
            # Apenas verifica se precisa atualizar, não força
            self.data_manager.get_data()
            self._schedule_next_check()

        # Verificar a cada 15 segundos (ainda menos frequente)
        self.root.after(15000, check_and_update)

    def _on_closing(self) -> None:
        """Manipula fechamento da aplicação"""
        try:
            self.event_manager.publish(
                Event(
                    EventType.LOG_MESSAGE,
                    {
                        "entry": LogEntry(
                            LogLevel.SISTEMA, "Encerrando aplicação...", component="GUI"
                        )
                    },
                )
            )

            # Parar monitoramento de contexto
            if "bot_control" in self.components:
                self.components["bot_control"]._stop_context_monitoring()

            # Parar bot se estiver rodando
            try:
                from ui import controller

                controller.encerrar_bot()
            except Exception:
                pass

            # Limpar recursos do sistema de dados
            if hasattr(self.data_manager, "cleanup"):
                self.data_manager.cleanup()

        except Exception:
            pass

        self.root.destroy()

    def run(self) -> None:
        """Executa a interface"""
        self.root.mainloop()


def iniciar_interface() -> None:
    """Função principal para iniciar a interface"""
    try:
        print("🚀 Iniciando SimpleMMO Bot v3.0...")
        app = ModernBotGUI()
        print("✅ Interface criada com sucesso!")
        app.run()
    except Exception as e:
        print(f"❌ Erro fatal ao iniciar interface: {e}")
        print(f"📍 Tipo do erro: {type(e).__name__}")
        import traceback

        traceback.print_exc()
        messagebox.showerror("Erro Fatal", f"Falha ao iniciar aplicação: {e}")


def main() -> None:
    """Função main para execução direta"""
    iniciar_interface()


if __name__ == "__main__":
    main()
