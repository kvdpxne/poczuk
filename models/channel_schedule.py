"""
Model danych dla harmonogramu czyszczenia kanału
"""
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ChannelSchedule:
    """Model reprezentujący harmonogram czyszczenia kanału"""
    channel_id: int
    channel_name: str
    time: str  # format HH:MM
    added_by: int
    added_at: datetime
    send_confirmation: bool = True

    def to_dict(self) -> dict:
        """Konwertuje obiekt do słownika"""
        return {
            "channel_id": self.channel_id,
            "channel_name": self.channel_name,
            "time": self.time,
            "added_by": self.added_by,
            "added_at": self.added_at.isoformat(),
            "send_confirmation": self.send_confirmation  # Dodajemy nowe pole
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ChannelSchedule':
        """Tworzy obiekt ze słownika"""
        return cls(
            channel_id=data["channel_id"],
            channel_name=data["channel_name"],
            time=data["time"],
            added_by=data["added_by"],
            added_at=datetime.fromisoformat(data["added_at"]),
            send_confirmation=data.get("send_confirmation", True)  # Domyślnie True dla kompatybilności
        )

    def matches_current_time(self, current_time: str) -> bool:
        """Sprawdza czy harmonogram pasuje do podanego czasu"""
        return self.time == current_time
