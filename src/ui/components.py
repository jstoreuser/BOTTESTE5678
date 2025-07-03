"""
SimpleMMO Bot - Componentes da Interface (Versão Simplificada)

Este módulo contém os componentes modulares da interface do usuário,
cada um responsável por uma funcionalidade específica.
"""

from datetime import datetime
import os
import subprocess
import threading
import time
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any, Dict, List

from .base import (
    BotConfiguration,
    Event,
    EventManager,
    EventType,
    LogEntry,
    LogLevel,
    UIComponent,
)


class HeaderComponent(UIComponent):
    """Componente do cabeçalho"""

    def _setup_ui(self) -> None:
        self.frame = tk.Frame(self.parent, bg="#2c3e50", height=60)
        self.frame.pack(fill="x", padx=5, pady=5)
        self.frame.pack_propagate(False)

        # Título
        title_label = tk.Label(
            self.frame,
            text="🎮 SimpleMMO Bot v3.1 - Simplificado",
            font=("Arial", 14, "bold"),
            fg="white",
            bg="#2c3e50",
        )
        title_label.pack(side="left", padx=15, pady=20)

        # Status do sistema
        self.system_status_var = tk.StringVar(value="🟢 Sistema Inicializado")
        status_label = tk.Label(
            self.frame,
            textvariable=self.system_status_var,
            font=("Arial", 10),
            fg="white",
            bg="#2c3e50",
        )
        status_label.pack(side="right", padx=15, pady=20)

    def _setup_events(self) -> None:
        """Configura eventos do componente"""
        self.event_manager.subscribe(EventType.BOT_STATUS_CHANGED, self)

    def handle_event(self, event: Event) -> None:
        """Processa eventos do sistema"""
        if event.type == EventType.BOT_STATUS_CHANGED:
            status = event.data.get("status")
            if status == "running":
                self.system_status_var.set("🟢 Bot em execução")
            elif status == "stopped":
                self.system_status_var.set("🔴 Bot parado")
            elif status == "paused":
                self.system_status_var.set("⏸️ Bot pausado")


class BotControlComponent(UIComponent):
    """Componente de controle do bot"""

    def _setup_ui(self) -> None:
        self.frame = ttk.LabelFrame(self.parent, text="🎮 Controle do Bot", padding=10)

        # Área de status do bot
        status_frame = ttk.Frame(self.frame)
        status_frame.pack(fill="x", pady=(0, 15))

        self.bot_status_var = tk.StringVar(value="⏸️ Bot Parado")
        status_label = ttk.Label(
            status_frame, textvariable=self.bot_status_var, font=("Arial", 12, "bold")
        )
        status_label.pack(anchor="w")

        # Área de modos de automação
        modes_frame = ttk.LabelFrame(self.frame, text="⚙️ Modos", padding=10)
        modes_frame.pack(fill="x", pady=(0, 15))

        # Modo de ataque
        self.attack_mode_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            modes_frame,
            text="⚔️ Modo de Ataque",
            variable=self.attack_mode_var,
            command=self._update_attack_mode,
        ).pack(anchor="w", pady=2)

        # Modo de coleta
        self.gather_mode_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            modes_frame,
            text="⛏️ Modo de Coleta",
            variable=self.gather_mode_var,
            command=self._update_gather_mode,
        ).pack(anchor="w", pady=2)

        # Botões de ação
        button_frame = ttk.Frame(self.frame)
        button_frame.pack(fill="x", pady=(10, 5))

        # Browser
        ttk.Button(
            button_frame,
            text="🌐 Abrir Browser",
            command=self._open_browser,
        ).pack(side="left", padx=(0, 10))

        # Start/Stop
        self.start_button = ttk.Button(
            button_frame,
            text="▶️ Iniciar Bot",
            command=self._start_bot,
        )
        self.start_button.pack(side="left", padx=(0, 10))

        self.stop_button = ttk.Button(
            button_frame,
            text="⏹️ Parar Bot",
            command=self._stop_bot,
            state="disabled",
        )
        self.stop_button.pack(side="left")

    def _setup_events(self) -> None:
        """Configura eventos do componente"""
        self.event_manager.subscribe(EventType.BOT_STATUS_CHANGED, self)

    def _update_attack_mode(self) -> None:
        """Atualiza modo de ataque."""
        enabled = self.attack_mode_var.get()
        try:
            from core.context import atualizar_configuracao

            atualizar_configuracao("modo_attack_ativo", enabled)
            self.publish_event(
                EventType.LOG_MESSAGE,
                {
                    "entry": LogEntry(
                        LogLevel.INFO,
                        f"{'✅' if enabled else '❌'} Modo de ataque {'ativado' if enabled else 'desativado'}",
                        component="BotControl",
                    )
                },
            )
        except Exception as e:
            self.publish_event(
                EventType.LOG_MESSAGE,
                {
                    "entry": LogEntry(
                        LogLevel.ERROR,
                        f"Erro ao atualizar modo de ataque: {e}",
                        component="BotControl",
                    )
                },
            )

    def _update_gather_mode(self) -> None:
        """Atualiza modo de coleta."""
        enabled = self.gather_mode_var.get()
        try:
            from core.context import atualizar_configuracao

            atualizar_configuracao("modo_coleta_ativo", enabled)
            self.publish_event(
                EventType.LOG_MESSAGE,
                {
                    "entry": LogEntry(
                        LogLevel.INFO,
                        f"{'✅' if enabled else '❌'} Modo de coleta {'ativado' if enabled else 'desativado'}",
                        component="BotControl",
                    )
                },
            )
        except Exception as e:
            self.publish_event(
                EventType.LOG_MESSAGE,
                {
                    "entry": LogEntry(
                        LogLevel.ERROR,
                        f"Erro ao atualizar modo de coleta: {e}",
                        component="BotControl",
                    )
                },
            )

    def _open_browser(self) -> None:
        """Abre o navegador para o SimpleMMO."""
        try:
            # Primeiro, tentar abrir o Brave Browser externamente
            from driver.manager import abrir_brave_browser

            if abrir_brave_browser():
                self.publish_event(
                    EventType.LOG_MESSAGE,
                    {
                        "entry": LogEntry(
                            LogLevel.INFO,
                            "Brave Browser aberto. Aguarde alguns segundos e tente conectar...",
                            component="BotControl",
                        )
                    },
                )

                # Aguardar um pouco para o browser inicializar
                time.sleep(2)

                # Tentar conectar ao browser
                from driver.manager import iniciar_driver

                driver = iniciar_driver()

                if driver:
                    self.publish_event(
                        EventType.LOG_MESSAGE,
                        {
                            "entry": LogEntry(
                                LogLevel.INFO,
                                "✅ Conectado ao navegador com sucesso!",
                                component="BotControl",
                            )
                        },
                    )
                else:
                    self.publish_event(
                        EventType.LOG_MESSAGE,
                        {
                            "entry": LogEntry(
                                LogLevel.WARNING,
                                "⚠️ Navegador aberto, mas não foi possível conectar automaticamente. Faça login e tente novamente.",
                                component="BotControl",
                            )
                        },
                    )
            else:
                self.publish_event(
                    EventType.LOG_MESSAGE,
                    {
                        "entry": LogEntry(
                            LogLevel.ERROR,
                            "❌ Erro ao abrir Brave Browser. Verifique se está instalado.",
                            component="BotControl",
                        )
                    },
                )

        except Exception as e:
            self.publish_event(
                EventType.LOG_MESSAGE,
                {
                    "entry": LogEntry(
                        LogLevel.ERROR,
                        f"Erro ao abrir navegador: {e}",
                        component="BotControl",
                    )
                },
            )

    def _start_bot(self) -> None:
        """Inicia o bot em thread separada."""
        if not self._check_browser_open():
            return

        try:
            from core.context import (
                atualizar_configuracao,
                definir_bot_rodando,
                obter_bot_rodando,
            )
            from ui.controller import iniciar_bot

            # Verificar se já está rodando
            if obter_bot_rodando():
                messagebox.showinfo("Aviso", "O bot já está em execução!")
                return

            # Marcar como rodando e limpar flag de finalização
            definir_bot_rodando(True)
            atualizar_configuracao("finalizar_bot", False)

            # Atualizar UI
            self.bot_status_var.set("🟢 Bot Ativo")
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")

            # Iniciar bot em thread separada
            def run_bot():
                try:
                    iniciar_bot()
                except Exception as e:
                    self.publish_event(
                        EventType.LOG_MESSAGE,
                        {
                            "entry": LogEntry(
                                LogLevel.ERROR,
                                f"Erro durante execução do bot: {e}",
                                component="BotControl",
                            )
                        },
                    )
                finally:
                    # Marcar como não rodando e atualizar UI quando o bot parar
                    from core.context import definir_bot_rodando

                    definir_bot_rodando(False)
                    self.bot_status_var.set("⏸️ Bot Parado")
                    self.start_button.config(state="normal")
                    self.stop_button.config(state="disabled")

            bot_thread = threading.Thread(target=run_bot, daemon=True)
            bot_thread.start()

            # Notificar sistema
            self.publish_event(
                EventType.BOT_STATUS_CHANGED,
                {"status": "running", "component": "BotControl"},
            )
        except Exception as e:
            self.publish_event(
                EventType.LOG_MESSAGE,
                {
                    "entry": LogEntry(
                        LogLevel.ERROR,
                        f"Erro ao iniciar bot: {e}",
                        component="BotControl",
                    )
                },
            )
            self._stop_bot()

    def _stop_bot(self) -> None:
        """Para o bot."""
        try:
            from core.context import (
                atualizar_configuracao,
                definir_bot_rodando,
                obter_bot_rodando,
            )

            if obter_bot_rodando():
                # Marcar bot como não rodando e sinalizar finalização
                definir_bot_rodando(False)
                atualizar_configuracao("finalizar_bot", True)

            # Atualizar UI
            self.bot_status_var.set("⏸️ Bot Parado")
            self.start_button.config(state="normal")
            self.stop_button.config(state="disabled")

            # Notificar sistema
            self.publish_event(
                EventType.BOT_STATUS_CHANGED,
                {"status": "stopped", "component": "BotControl"},
            )

            # Log
            self.publish_event(
                EventType.LOG_MESSAGE,
                {
                    "entry": LogEntry(
                        LogLevel.INFO,
                        "Bot parado pelo usuário",
                        component="BotControl",
                    )
                },
            )
        except Exception as e:
            self.publish_event(
                EventType.LOG_MESSAGE,
                {
                    "entry": LogEntry(
                        LogLevel.ERROR,
                        f"Erro ao parar bot: {e}",
                        component="BotControl",
                    )
                },
            )

    def _check_browser_open(self) -> bool:
        """Verifica se o navegador está aberto e funcionando."""
        from driver.manager import get_driver

        driver = get_driver()
        if not driver:
            messagebox.showwarning(
                "Atenção",
                "Navegador não está conectado!\n\nPor favor:\n1. Clique em 'Abrir Browser'\n2. Faça login no SimpleMMO\n3. Tente novamente",
            )
            return False

        # Testar se o driver está realmente funcionando
        try:
            # Tentar acessar uma propriedade do driver
            _ = driver.current_url
            return True
        except Exception:
            messagebox.showwarning(
                "Atenção",
                "Conexão com navegador perdida!\n\nPor favor:\n1. Clique em 'Abrir Browser' novamente\n2. Faça login no SimpleMMO\n3. Tente novamente",
            )
            return False

    def _sync_ui_with_context(self) -> None:
        """Sincroniza a UI com as configurações do contexto."""
        try:
            from core.context import obter_configuracao

            # Atualizar checkboxes com valores do contexto
            attack_enabled = obter_configuracao("modo_attack_ativo")
            gather_enabled = obter_configuracao("modo_coleta_ativo")

            self.attack_mode_var.set(attack_enabled)
            self.gather_mode_var.set(gather_enabled)

        except Exception as e:
            self.publish_event(
                EventType.LOG_MESSAGE,
                {
                    "entry": LogEntry(
                        LogLevel.ERROR,
                        f"Erro ao sincronizar UI: {e}",
                        component="BotControl",
                    )
                },
            )

    def handle_event(self, event: Event) -> None:
        """Processa eventos do sistema"""
        if event.type == EventType.BOT_STATUS_CHANGED:
            status = event.data.get("status")
            sender = event.data.get("component", "")

            # Evitar loop infinito
            if sender == "BotControl":
                return

            if status == "running":
                self.bot_status_var.set("🟢 Bot Ativo")
                self.start_button.config(state="disabled")
                self.stop_button.config(state="normal")
            elif status == "stopped":
                self.bot_status_var.set("⏸️ Bot Parado")
                self.start_button.config(state="normal")
                self.stop_button.config(state="disabled")
                # Sincronizar UI quando o bot parar
                self._sync_ui_with_context()


class LogComponent(UIComponent):
    """Componente de logs"""

    def __init__(self, parent: tk.Widget, event_manager: EventManager) -> None:
        super().__init__(parent, event_manager)
        self.log_entries: List[LogEntry] = []

    def _setup_ui(self) -> None:
        self.frame = ttk.Frame(self.parent)

        # Controles
        self._setup_controls()

        # Área de logs
        self._setup_log_area()

    def _setup_controls(self) -> None:
        """Configura controles do componente"""
        controls_frame = ttk.Frame(self.frame)
        controls_frame.pack(fill="x", pady=(0, 10))

        ttk.Button(controls_frame, text="🗑️ Limpar", command=self._clear_logs).pack(
            side="left", padx=(0, 10)
        )

        ttk.Button(controls_frame, text="💾 Salvar", command=self._save_logs).pack(
            side="left", padx=(0, 20)
        )

        # Filtro de nível
        ttk.Label(controls_frame, text="Filtro:").pack(side="left", padx=(0, 5))

        self.filter_var = tk.StringVar(value="TODOS")
        filter_combo = ttk.Combobox(
            controls_frame,
            textvariable=self.filter_var,
            values=[
                "TODOS",
                "SISTEMA",
                "BOT",
                "INFO",
                "ERROR",
                "WARNING",
                "DEBUG",
            ],
            state="readonly",
            width=12,
        )
        filter_combo.pack(side="left")
        filter_combo.bind("<<ComboboxSelected>>", self._apply_filter)

    def _setup_log_area(self) -> None:
        """Configura área de logs"""
        log_frame = ttk.Frame(self.frame)
        log_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Text widget com scrollbar
        self.log_text = tk.Text(
            log_frame,
            height=20,
            wrap=tk.WORD,
            font=("Consolas", 9),
            bg="#1e1e1e",
            fg="#ffffff",
            insertbackground="#ffffff",
            selectbackground="#264f78",
        )

        scrollbar = ttk.Scrollbar(
            log_frame, orient="vertical", command=self.log_text.yview
        )
        self.log_text.configure(yscrollcommand=scrollbar.set)

        self.log_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Tags para colorir os logs
        self.log_text.tag_configure("ERROR", foreground="#ff6347")  # Vermelho
        self.log_text.tag_configure("WARNING", foreground="#ffa500")  # Laranja
        self.log_text.tag_configure("INFO", foreground="#add8e6")  # Azul claro
        self.log_text.tag_configure("DEBUG", foreground="#90ee90")  # Verde claro
        self.log_text.tag_configure("BOT", foreground="#ffff00")  # Amarelo
        self.log_text.tag_configure("SISTEMA", foreground="#ff69b4")  # Rosa
        self.log_text.tag_configure("timestamp", foreground="#888888")  # Cinza

    def _setup_events(self) -> None:
        """Configura eventos do componente"""
        self.event_manager.subscribe(EventType.LOG_MESSAGE, self)

    def _clear_logs(self) -> None:
        """Limpa todos os logs"""
        self.log_text.delete(1.0, tk.END)
        self.log_entries = []

    def _save_logs(self) -> None:
        """Salva os logs em um arquivo"""
        try:
            filename = f"logs_bot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                for entry in self.log_entries:
                    f.write(entry.format() + "\n")

            messagebox.showinfo("Sucesso", f"Logs salvos em {filename}")

        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar logs: {e}")

    def _apply_filter(self, event=None) -> None:
        """Aplica filtro aos logs"""
        self.log_text.delete(1.0, tk.END)
        current_filter = self.filter_var.get()

        # Mostrar logs filtrados
        for entry in self.log_entries:
            if current_filter == "TODOS" or entry.level.display_name == current_filter:
                self._insert_formatted_entry(entry)

        self.log_text.see(tk.END)

    def _insert_formatted_entry(self, entry: LogEntry) -> None:
        """Insere entrada formatada no log"""
        # Timestamp - com validação adicional
        try:
            if entry.timestamp is None or not isinstance(entry.timestamp, (int, float)):
                timestamp_str = time.strftime("%H:%M:%S")
            else:
                timestamp_str = time.strftime(
                    "%H:%M:%S", time.localtime(entry.timestamp)
                )
        except (ValueError, OSError, TypeError):
            timestamp_str = time.strftime("%H:%M:%S")

        self.log_text.insert(tk.END, f"[{timestamp_str}] ", "timestamp")

        # Nível
        self.log_text.insert(
            tk.END, f"[{entry.level.display_name}] ", entry.level.display_name
        )

        # Componente (se existir)
        if entry.component:
            self.log_text.insert(
                tk.END, f"[{entry.component}] ", entry.level.display_name
            )

        # Mensagem
        self.log_text.insert(tk.END, f"{entry.message}\n", entry.level.display_name)

        # Auto-scroll para a última linha
        self.log_text.see(tk.END)

    def _update_last_line_with_count(self, entry: LogEntry) -> None:
        """Atualiza a última linha do log com contador"""

        def ui_update():
            try:
                # Verificar filtro
                current_filter = self.filter_var.get()
                if (
                    current_filter != "TODOS"
                    and entry.level.display_name != current_filter
                ):
                    return

                # Remover última linha
                self.log_text.delete("end-2l", "end-1l")

                # Inserir linha atualizada
                self._insert_formatted_entry(entry)

            except Exception as e:
                print(f"Erro ao atualizar última linha: {e}")

        self.parent.after(0, ui_update)

    def _update_log_display(self, entry: LogEntry) -> None:
        """Atualiza display do log com formatação melhorada"""

        def ui_update():
            try:
                # Verificar filtro
                current_filter = self.filter_var.get()
                if (
                    current_filter != "TODOS"
                    and entry.level.display_name != current_filter
                ):
                    return

                self._insert_formatted_entry(entry)

                # Limitar linhas visíveis
                lines = int(self.log_text.index("end-1c").split(".")[0])
                if lines > 200:
                    self.log_text.delete("1.0", "2.0")

                # Auto-scroll se estiver perto do final
                if (
                    float(self.log_text.index("end-2c"))
                    - float(self.log_text.index("@0,0"))
                    < 40
                ):
                    self.log_text.see(tk.END)

            except Exception as e:
                print(f"Erro ao atualizar log display: {e}")

        self.parent.after(0, ui_update)

    def handle_event(self, event: Event) -> None:
        """Processa eventos do sistema"""
        if event.type == EventType.LOG_MESSAGE:
            entry = event.data.get("entry")
            if not entry or not isinstance(entry, LogEntry):
                return

            # Armazenar a entrada
            self.log_entries.append(entry)

            # Verificar se é uma atualização de uma linha existente
            if event.data.get("update_last", False):
                self._update_last_line_with_count(entry)
            else:
                self._update_log_display(entry)
