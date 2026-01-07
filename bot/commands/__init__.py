"""
Inicjalizacja modułów komend
"""
from .avatar import AvatarCommand
from .coinflip import CoinflipCommand
from .delete_nickname import DeleteNicknameCommand
from .help import HelpCommand
from .set_nickname import SetNicknameCommand
from .uptime import UptimeCommand
from .ping import PingCommand

__all__ = [
    'AvatarCommand',
    'PingCommand',
    'CoinflipCommand',
    'DeleteNicknameCommand',
    'SetNicknameCommand',
    'UptimeCommand',
    'HelpCommand',
]
