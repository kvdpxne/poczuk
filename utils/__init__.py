# Dodaj logger do eksportowanych modułów
from .logger import (
    get_logger,
    log_command,
    log_error,
)

__all__ = [
    'get_logger',
    'log_command',
    'log_error',
]