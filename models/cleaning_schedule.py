"""
Model danych dla harmonogramu czyszczenia kanału - Single Responsibility Principle
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class CleaningSchedule:
    """Model reprezentujący harmonogram czyszczenia kanału"""
    channel_id: int
    channel_name: str
    time: str
    added_by: int
    added_at: datetime
    guild_id: Optional[int] = None
    frequency_id: int = 1
    is_active: bool = True
    exclude_pinned: bool = True
    last_run_at: Optional[datetime] = None
    schedule_id: Optional[int] = None

    def to_dict(self) -> dict:
        """Konwertuje obiekt do słownika"""
        return {
            "channel_id": self.channel_id,
            "channel_name": self.channel_name,
            "time": self.time,
            "added_by": self.added_by,
            "added_at": self.added_at.isoformat(),
            "guild_id": self.guild_id,
            "frequency_id": self.frequency_id,
            "is_active": self.is_active,
            "exclude_pinned": self.exclude_pinned,
            "last_run_at": self.last_run_at.isoformat() if self.last_run_at else None,
            "schedule_id": self.schedule_id
        }

    def matches_current_time(self, current_time: str) -> bool:
        """Sprawdza czy harmonogram pasuje do podanego czasu"""
        return self.time == current_time and self.is_active