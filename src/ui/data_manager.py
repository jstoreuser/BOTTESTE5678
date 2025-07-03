"""
SimpleMMO Bot - Gerenciador de Dados

Este módulo fornece o gerenciamento centralizado de dados do player,
incluindo extração via Selenium, cache inteligente e sistema de eventos.
"""

import re
import threading
import time
from typing import Optional

from selenium.webdriver.common.by import By

from .base import (
    DataProvider,
    Event,
    EventManager,
    EventType,
    LogEntry,
    LogLevel,
    PlayerData,
)


class PlayerDataExtractor(DataProvider):
    """Extrator de dados do player via Selenium com verificação inteligente"""

    def __init__(self, event_manager: EventManager):
        self.event_manager = event_manager
        self._last_data: Optional[PlayerData] = None
        self._last_update = 0
        self._cache_duration = 10  # Aumentado para 10 segundos
        self._is_updating = False
        self._update_lock = threading.Lock()
        self._last_popup_check = 0
        self._popup_check_interval = (
            5  # Verificar popup a cada 5 segundos (menos frequente)
        )
        self._popup_available = False
        self._driver = None  # Driver compartilhado
        self._driver_lock = threading.Lock()  # Lock para acesso ao driver

        # Registrar para receber notificações de ações do bot
        self._register_action_callback()

    def _register_action_callback(self) -> None:
        """Registra callback para receber notificações de ações"""
        try:
            from core import context

            context.registrar_callback_atualizacao_dados(self._on_bot_action)
        except Exception as e:
            self._log(f"Erro ao registrar callback de ações: {e}", LogLevel.DEBUG)

    def _on_bot_action(self, action_name: str) -> None:
        """Callback chamado quando o bot executa uma ação"""
        # Lista de ações que requerem atualização de dados
        acoes_que_atualizam_dados = [
            "Attack",
            "Gather",
            "Fight",
            "Heal",
            "Travel",
            "Step",
        ]

        # Verifica se a ação requer atualização de dados
        if any(
            acao.lower() in action_name.lower() for acao in acoes_que_atualizam_dados
        ):
            self._log(
                f"Ação detectada que requer atualização: {action_name}", LogLevel.DEBUG
            )
            # Solicita atualização após pequeno delay
            threading.Timer(2.0, self.force_update).start()

    def get_data(self) -> Optional[PlayerData]:
        """Obtém dados do player (com cache inteligente)"""
        current_time = time.time()

        # Retorna cache se ainda válido
        if (
            current_time - self._last_update
        ) < self._cache_duration and self._last_data:
            return self._last_data

        # Só atualiza se popup estiver disponível
        if (
            self._should_check_popup()
            and self._check_popup_available()
            and not self._is_updating
        ):
            self._update_async()
        elif self._last_data:
            # Se popup não está disponível, retorna último dado válido
            return self._last_data

        return self._last_data

    def _should_check_popup(self) -> bool:
        """Verifica se deve checar se popup está disponível"""
        current_time = time.time()
        return (current_time - self._last_popup_check) > self._popup_check_interval

    def _get_driver(self):
        """Obtém ou cria driver compartilhado"""
        with self._driver_lock:
            if self._driver is None:
                from selenium import webdriver
                from selenium.webdriver.chrome.options import Options

                options = Options()
                options.debugger_address = "127.0.0.1:9222"
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")

                try:
                    self._driver = webdriver.Chrome(options=options)
                    self._driver.set_page_load_timeout(5)
                except Exception as e:
                    self._log(f"Erro ao criar driver: {e}", LogLevel.ERROR)
                    return None

            return self._driver

    def _check_popup_available(self) -> bool:
        """Verifica rapidamente se popup está disponível sem logar"""
        current_time = time.time()
        self._last_popup_check = current_time

        try:
            driver = self._get_driver()
            if driver is None:
                self._popup_available = False
                return False

            self._popup_available = self._check_popup_open(driver)
            return self._popup_available

        except Exception:
            self._popup_available = False
            # Se houve erro, limpar driver para tentar recriar na próxima vez
            with self._driver_lock:
                if self._driver:
                    try:
                        self._driver.quit()
                    except Exception:
                        pass
                    self._driver = None
            return False

    def is_available(self) -> bool:
        """Verifica se dados estão disponíveis"""
        return self._last_data is not None and self._last_data.status == "success"

    def force_update(self) -> None:
        """Força atualização dos dados (só se popup estiver disponível)"""
        if self._check_popup_available():
            self._update_async()
        else:
            self._log("Popup não está disponível para extração", LogLevel.DEBUG)

    def request_update_after_action(self, action_name: str) -> None:
        """Solicita atualização após uma ação específica do bot"""
        self._log(f"Solicitando atualização após: {action_name}", LogLevel.DEBUG)
        # Pequeno delay para permitir que a ação seja processada
        threading.Timer(1.0, self.force_update).start()

    def _update_async(self) -> None:
        """Atualiza dados em thread separada (só se popup disponível)"""

        def worker():
            with self._update_lock:
                if self._is_updating:
                    return
                self._is_updating = True

            try:
                # Verificação dupla antes de extrair
                if not self._popup_available:
                    self._log(
                        "Popup não disponível, cancelando extração", LogLevel.DEBUG
                    )
                    return

                self._log("Iniciando extração de dados do player", LogLevel.DADOS)
                data = self._extract_player_data()

                self._last_data = data
                self._last_update = time.time()

                # Publica evento de atualização
                self._publish_event(
                    EventType.PLAYER_DATA_UPDATED,
                    {"data": data, "timestamp": self._last_update},
                )

                if data.status == "success":
                    self._log("Dados do player extraídos com sucesso", LogLevel.DADOS)
                else:
                    self._log(
                        f"Falha na extração: {data.error_message}", LogLevel.ERROR
                    )

            except Exception as e:
                error_data = PlayerData(
                    status="error", error_message=str(e), last_updated=time.time()
                )
                self._last_data = error_data
                self._log(f"Erro na extração de dados: {e}", LogLevel.ERROR)

                self._publish_event(
                    EventType.ERROR_OCCURRED,
                    {"error": str(e), "component": "PlayerDataExtractor"},
                )
            finally:
                self._is_updating = False

        threading.Thread(target=worker, daemon=True).start()

    def _extract_player_data(self) -> PlayerData:
        """Extrai dados do player via Selenium"""
        try:
            driver = self._get_driver()
            if driver is None:
                return PlayerData(
                    status="driver_error",
                    error_message="Não foi possível conectar ao Chrome",
                    last_updated=time.time(),
                )

            # Verificar se popup de stats está aberto
            if not self._check_popup_open(driver):
                return PlayerData(
                    status="popup_closed",
                    error_message="Popup de stats não encontrado",
                    last_updated=time.time(),
                )

            # Extrair dados usando seletores
            raw_data = self._extract_raw_data(driver)

            # Converter para PlayerData
            return self._create_player_data(raw_data)

        except Exception as e:
            # Se houve erro, limpar driver
            with self._driver_lock:
                if self._driver:
                    try:
                        self._driver.quit()
                    except Exception:
                        pass
                    self._driver = None

            return PlayerData(
                status="error", error_message=str(e), last_updated=time.time()
            )

    def _check_popup_open(self, driver) -> bool:
        """Verifica se o popup de stats está aberto"""
        popup_selectors = [
            "div.rounded-lg.ring-1.ring-black.ring-opacity-5",
            "div[class*='ring-1'][class*='ring-black']",
            "div[class*='popup']",
        ]

        for selector in popup_selectors:
            try:
                popups = driver.find_elements(By.CSS_SELECTOR, selector)
                for popup in popups:
                    if popup.is_displayed() and (
                        "Health" in popup.text or "HP" in popup.text
                    ):
                        return True
            except Exception:
                continue

        return False

    def _extract_raw_data(self, driver) -> dict:
        """Extrai dados brutos usando seletores CSS"""
        selectors = {
            "health": "[x-text*='user.current_hp']",
            "max_health": "[x-text='user.max_hp']",
            "energy": "[x-text='user.energy']",
            "max_energy": "[x-text='user.max_energy']",
            "gold": "[x-text='user.gold']",
            "bank": "[x-text='user.bank']",
            "diamonds": "[x-text='user.diamonds']",
            "quest_points": "[x-text='user.quest_points']",
            "max_quest_points": "[x-text='user.max_quest_points']",
            "steps": "[x-text='user.total_steps']",
            "level": "[x-text='user.level']",
            "exp_remaining": "[x-text='user.exp_remaining']",
        }

        data = {}

        for key, selector in selectors.items():
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed():
                        text = element.text.strip()
                        if text:
                            # Extrair número do texto
                            cleaned = re.sub(r"[,.]", "", text)
                            match = re.search(r"\d+", cleaned)
                            if match:
                                data[key] = int(match.group())
                                break
            except Exception:
                data[key] = 0

        return data

    def _create_player_data(self, raw_data: dict) -> PlayerData:
        """Cria objeto PlayerData a partir dos dados brutos"""
        return PlayerData(
            health=raw_data.get("health", 0),
            max_health=raw_data.get("max_health", 0),
            energy=raw_data.get("energy", 0),
            max_energy=raw_data.get("max_energy", 0),
            quest_points=raw_data.get("quest_points", 0),
            max_quest_points=raw_data.get("max_quest_points", 0),
            gold=raw_data.get("gold", 0),
            bank=raw_data.get("bank", 0),
            diamonds=raw_data.get("diamonds", 0),
            level=raw_data.get("level", 0),
            exp_remaining=raw_data.get("exp_remaining", 0),
            steps=raw_data.get("steps", 0),
            status="success",
            last_updated=time.time(),
        )

    def _log(self, message: str, level: LogLevel) -> None:
        """Envia log via eventos"""
        log_entry = LogEntry(
            level=level, message=message, component="PlayerDataExtractor"
        )

        self._publish_event(EventType.LOG_MESSAGE, {"entry": log_entry})

    def _publish_event(self, event_type: EventType, data: dict) -> None:
        """Publica evento"""
        event = Event(type=event_type, data=data)
        self.event_manager.publish(event)

    def cleanup(self) -> None:
        """Limpa recursos (driver) ao finalizar"""
        # Desregistrar callback
        try:
            from core import context

            context.remover_callback_atualizacao_dados(self._on_bot_action)
        except Exception as e:
            self._log(f"Erro ao desregistrar callback: {e}", LogLevel.DEBUG)

        # Limpar driver
        with self._driver_lock:
            if self._driver:
                try:
                    self._driver.quit()
                    self._log("Driver do Chrome fechado", LogLevel.DEBUG)
                except Exception as e:
                    self._log(f"Erro ao fechar driver: {e}", LogLevel.DEBUG)
                finally:
                    self._driver = None

    def __del__(self):
        """Destrutor - garante limpeza dos recursos"""
        try:
            self.cleanup()
        except Exception:
            pass


class DataManager:
    """Gerenciador centralizado de todos os dados com atualizações inteligentes"""

    def __init__(self, event_manager: EventManager):
        self.event_manager = event_manager
        self.player_extractor = PlayerDataExtractor(event_manager)
        self._last_manual_update = 0
        self._manual_update_cooldown = 5  # 5 segundos entre updates manuais

    def get_player_data(self) -> Optional[PlayerData]:
        """Obtém dados do player"""
        return self.player_extractor.get_data()

    def force_player_update(self) -> None:
        """Força atualização dos dados do player (com cooldown)"""
        current_time = time.time()
        if (current_time - self._last_manual_update) > self._manual_update_cooldown:
            self._last_manual_update = current_time
            self.player_extractor.force_update()
        else:
            self._log("Update manual em cooldown", LogLevel.DEBUG)

    def request_update_after_bot_action(self, action: str) -> None:
        """Solicita atualização após ação do bot"""
        self.player_extractor.request_update_after_action(action)

    def is_player_data_available(self) -> bool:
        """Verifica se dados do player estão disponíveis"""
        return self.player_extractor.is_available()

    def _log(self, message: str, level: LogLevel) -> None:
        """Envia log via eventos"""
        log_entry = LogEntry(level=level, message=message, component="DataManager")
        event = Event(type=EventType.LOG_MESSAGE, data={"entry": log_entry})
        self.event_manager.publish(event)
