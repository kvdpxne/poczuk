"""
Walidatory danych
"""
from datetime import datetime


class TimeValidator:
    """Walidacja czasu i danych"""
    
    @staticmethod
    def validate_time_format(time_str: str) -> bool:
        """Sprawdza poprawność formatu czasu HH:MM"""
        try:
            datetime.strptime(time_str, "%H:%M")
            return True
        except ValueError:
            return False
    
    @staticmethod
    def get_current_time() -> str:
        """Zwraca aktualny czas w formacie HH:MM"""
        return datetime.now().strftime("%H:%M")
    
    @staticmethod
    def is_valid_channel_id(channel_id: int) -> bool:
        """Sprawdza czy ID kanału jest poprawne"""
        return isinstance(channel_id, int) and channel_id > 0
