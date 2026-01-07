"""
Zaawansowany system logowania do plików dziennych
"""
import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
import sys


class DailyFileHandler(logging.Handler):
    """Handler tworzący nowy plik logów każdego dnia"""

    def __init__(self, log_directory='logs'):
        super().__init__()
        self.log_directory = log_directory
        self.current_date = None
        self.current_handler = None

        # Utwórz katalog jeśli nie istnieje
        os.makedirs(log_directory, exist_ok=True)

    def emit(self, record):
        """Zapisuje log do odpowiedniego pliku dziennego"""
        today = datetime.now().date()

        # Jeśli zmienił się dzień lub handler nie istnieje
        if today != self.current_date or self.current_handler is None:
            self._switch_handler(today)

        # Przekaż rekord do aktualnego handlera
        if self.current_handler:
            self.current_handler.emit(record)

    def _switch_handler(self, date):
        """Przełącza handler na nowy plik dzienny"""
        # Zamknij poprzedni handler
        if self.current_handler:
            self.current_handler.close()

        # Utwórz nazwę pliku w formacie YYYY-MM-DD.log
        filename = os.path.join(self.log_directory, f"{date}.log")

        # Utwórz nowy handler dla pliku
        file_handler = RotatingFileHandler(
            filename,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )

        # Ustaw format dla handlera
        formatter = logging.Formatter(
            '%(asctime)s.%(msecs)04d | %(levelname)-8s | [%(name)s] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)

        self.current_handler = file_handler
        self.current_date = date

    def close(self):
        """Zamyka aktualny handler"""
        if self.current_handler:
            self.current_handler.close()
        super().close()


class DiscordBotLogger:
    """Główna klasa logera dla bota Discord"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.logger = logging.getLogger('discord_bot')
        self.logger.setLevel(logging.INFO)

        # Usuń istniejące handlery
        self.logger.handlers.clear()

        # Ustaw format dla wszystkich handlerów
        formatter = logging.Formatter(
            '%(asctime)s.%(msecs)04d | %(levelname)-8s | [%(name)s] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Handler konsolowy (stdout)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)

        # Handler dziennych plików
        daily_handler = DailyFileHandler('logs')
        daily_handler.setLevel(logging.INFO)
        daily_handler.setFormatter(formatter)

        # Handler dla błędów (stderr)
        error_handler = logging.StreamHandler(sys.stderr)
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)

        # Dodaj wszystkie handlery
        self.logger.addHandler(console_handler)
        self.logger.addHandler(daily_handler)
        self.logger.addHandler(error_handler)

        self._initialized = True

    def get_logger(self, name=None):
        """Zwraca loggera z konkretną nazwą"""
        if name:
            return logging.getLogger(name)
        return self.logger

    def setup_module_logger(self, module_name):
        """Konfiguruje logger dla konkretnego modułu"""
        logger = logging.getLogger(module_name)
        logger.setLevel(logging.INFO)
        return logger


# Funkcje pomocnicze
def get_module_logger(module_name):
    """Pobiera loggera dla danego modułu"""
    return DiscordBotLogger().get_logger(module_name)


def log_command(ctx):
    """Loguje wykonanie komendy"""
    logger = get_module_logger('commands')
    logger.info(
        f"Komenda: {ctx.command.name} | "
        f"Użytkownik: {ctx.author} ({ctx.author.id}) | "
        f"Kanał: {ctx.channel.name} ({ctx.channel.id}) | "
        f"Serwer: {ctx.guild.name} ({ctx.guild.id})"
    )


def log_schedule_execution(channel_id, channel_name, deleted_count):
    """Loguje wykonanie harmonogramu czyszczenia"""
    logger = get_module_logger('scheduler')
    logger.info(
        f"Wykonano harmonogram | "
        f"Kanał: {channel_name} ({channel_id}) | "
        f"Usunięto: {deleted_count} wiadomości"
    )


def log_error(module_name, error, context=None):
    """Loguje błąd z kontekstem"""
    logger = get_module_logger(module_name)
    error_msg = f"Błąd: {type(error).__name__}: {str(error)}"
    if context:
        error_msg += f" | Kontekst: {context}"
    logger.error(error_msg, exc_info=True)


def log_bot_start():
    """Loguje start bota"""
    logger = get_module_logger('main')
    logger.info("=" * 50)
    logger.info("Discord Channel Cleaner - Uruchamianie")
    logger.info("=" * 50)


def log_bot_ready(bot_user, guild_count, schedule_count):
    """Loguje gotowość bota"""
    logger = get_module_logger('main')
    logger.info(f"Bot zalogowany jako: {bot_user.name} ({bot_user.id})")
    logger.info(f"Liczba serwerów: {guild_count}")
    logger.info(f"Liczba harmonogramów: {schedule_count}")
    logger.info("=" * 50)