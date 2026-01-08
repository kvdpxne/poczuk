"""
Inicjalizacja modułów komend
"""
from .avatar import AvatarCommand
from .clean import CleanCommand
from .coinflip import CoinflipCommand
from .delete_nickname import DeleteNicknameCommand
from .help import HelpCommand
from .info import InfoCommand
from .purge import PurgeCommand
from .set_nickname import SetNicknameCommand
from .source_code import SourceCodeCommand
from .uptime import UptimeCommand
from .ping import PingCommand
from .version import VersionCommand
from .whois import WhoisCommand

__all__ = [
    'AvatarCommand',
    'PingCommand',
    'CoinflipCommand',
    'DeleteNicknameCommand',
    'HelpCommand',
    'InfoCommand',
    'SetNicknameCommand',
    'UptimeCommand',
    'VersionCommand',
    'WhoisCommand',
    'PurgeCommand',
    'SourceCodeCommand',
    'CleanCommand'
]


