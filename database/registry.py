"""
Rejestr wszystkich modeli SQLAlchemy dla uniknięcia cyklicznych importów
"""
from sqlalchemy.orm import registry

# Globalny rejestr mapperów
mapper_registry = registry()


# Funkcja do inicjalizacji wszystkich modeli
def configure_models():
    """Konfiguruje wszystkie modele w odpowiedniej kolejności"""
    # Import modeli w odpowiedniej kolejności
    from .models.action_type import ActionType
    from .models.frequency import Frequency
    from .models.guild_setting import GuildSetting
    from .models.user_setting import UserSetting
    from .models.schedule import Schedule
    from .models.debt import Debt
    from .models.debt_schedule import DebtSchedule
    from .models.log import Log

    # Zwróć listę wszystkich klas modeli
    return [
        ActionType,
        Frequency,
        GuildSetting,
        UserSetting,
        Schedule,
        Debt,
        DebtSchedule,
        Log
    ]