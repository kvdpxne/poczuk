from .avatar import AvatarCommand
from .clean import CleanCommand
from .coin_flip import CoinFlipCommand
from .delete_nickname import DeleteNicknameCommand
from .help import HelpCommand
from .info import InfoCommand
from .ping import PingCommand
from .purge import PurgeCommand
from .set_nickname import SetNicknameCommand
from .source_code import SourceCodeCommand
from .uptime import UptimeCommand
from .version import VersionCommand
from .whois import WhoisCommand

__all__ = [
    'AvatarCommand',
    'PingCommand',
    'CoinFlipCommand',
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
