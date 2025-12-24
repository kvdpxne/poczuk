"""
Model danych dla harmonogramu czyszczenia kanału
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ChannelSchedule:
    """Model reprezentujący harmonogram czyszczenia kanału"""
    channel_id: int
    channel_name: str
    time: str  # format HH:MM
    added_by: int
    added_at: datetime
    
    def to_dict(self) -> dict:
        """Konwertuje obiekt do słownika"""
        return {
            "channel_id": self.channel_id,
            "channel_name": self.channel_name,
            "time": self.time,
            "added_by": self.added_by,
            "added_at": self.added_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ChannelSchedule':
        """Tworzy obiekt ze słownika"""
        return cls(
            channel_id=data["channel_id"],
            channel_name=data["channel_name"],
            time=data["time"],
            added_by=data["added_by"],
            added_at=datetime.fromisoformat(data["added_at"])
        )
    
    def matches_current_time(self, current_time: str) -> bool:
        """Sprawdza czy harmonogram pasuje do podanego czasu"""
        return self.time == current_time
