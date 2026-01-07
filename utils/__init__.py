# Dodaj logger do eksportowanych modułów
from .logger import (
    DiscordBotLogger,
    get_module_logger,
    log_command,
    log_schedule_execution,
    log_error,
    log_bot_start,
    log_bot_ready
)

__all__ = [
    'DiscordBotLogger',
    'get_module_logger',
    'log_command',
    'log_schedule_execution',
    'log_error',
    'log_bot_start',
    'log_bot_ready'
]