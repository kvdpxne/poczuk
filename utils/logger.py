"""
Prosty, działający system logowania
"""
import logging
import os
import sys
from datetime import datetime, timezone
import time


class UTCFormatter(logging.Formatter):
    """Formatter konwertujący czas na UTC"""
    converter = time.gmtime  # Używa czasu UTC zamiast lokalnego

    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created, tz=timezone.utc)
        if datefmt:
            s = dt.strftime(datefmt)
        else:
            s = dt.strftime(self.default_time_format)
        return f"{s}.{record.msecs:03.0f}Z"  # Dodaj milisekundy i 'Z' na końcu


def setup_logging():
    """Konfiguruje system logowania - URUCHOMIĆ NA POCZĄTKU main.py"""

    # Utwórz katalog logów jeśli nie istnieje
    log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True)

    # Utwórz nazwę pliku z dzisiejszą datą (w UTC)
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    log_file = os.path.join(log_dir, f'{today}.log')

    # Utwórz formatter z czasem UTC
    formatter = UTCFormatter(
        fmt='%(asctime)s %(levelname)-8s %(process)d [%(threadName)-16s] %(name)-32s : %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Konfiguruj handlery
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)

    # Skonfiguruj root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Usuń istniejące handlery (jeśli są) i dodaj nasze
    root_logger.handlers = []
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    # Konfiguruj loggerów discord
    discord_loggers = [
        'discord',
        'discord.client',
        'discord.gateway',
        'discord.http',
        'discord.state',
        'discord.voice_state',
        'discord.voice_client',
        'discord.player'
    ]

    for logger_name in discord_loggers:
        discord_logger = logging.getLogger(logger_name)

        # Usuń wszystkie istniejące handlery z discord loggerów
        discord_logger.handlers = []

        # Dodaj nasze handlery z naszym formatterem
        discord_logger.addHandler(console_handler)
        discord_logger.addHandler(file_handler)

        # Wyłącz propagację do root loggera, żeby uniknąć duplikacji
        discord_logger.propagate = False

    # Pobierz loggera dla tej funkcji
    logger = logging.getLogger(__name__)
    logger.info("System logowania zainicjalizowany")
    logger.info(f"Logi zapisywane do: {log_file}")

    return logger

def get_logger(name):
    """Zwraca loggera o podanej nazwie"""
    return logging.getLogger(name)


# Funkcje pomocnicze dla łatwego logowania
def log_info(module, message):
    """Loguje wiadomość informacyjną"""
    logger = get_logger(module)
    logger.info(message)


def log_warning(module, message):
    """Loguje ostrzeżenie"""
    logger = get_logger(module)
    logger.warning(message)


def log_error(module, message, exc_info=False):
    """Loguje błąd"""
    logger = get_logger(module)
    logger.error(message, exc_info=exc_info)


def log_command(ctx):
    """Specjalna funkcja do logowania komend"""
    logger = get_logger('commands')
    logger.info(
        f"Komenda: {ctx.command.name} | "
        f"Użytkownik: {ctx.author} ({ctx.author.id}) | "
        f"Kanał: {ctx.channel.name} ({ctx.channel.id}) | "
        f"Serwer: {ctx.guild.name} ({ctx.guild.id})"
    )
