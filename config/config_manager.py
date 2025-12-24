"""
Zarządzanie konfiguracją
"""
import json
import os
from typing import List, Optional
from models.channel_schedule import ChannelSchedule


class ConfigManager:
    """Zarządza konfiguracją aplikacji"""
    
    def __init__(self, config_path: str = "data/config.json"):
        self.config_path = config_path
        self._ensure_data_directory()
    
    def _ensure_data_directory(self):
        """Tworzy katalog data jeśli nie istnieje"""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
    
    def load_schedules(self) -> List[ChannelSchedule]:
        """Ładuje harmonogramy z pliku"""
        if not os.path.exists(self.config_path):
            return []
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [ChannelSchedule.from_dict(item) for item in data.get("channels", [])]
        except (json.JSONDecodeError, KeyError):
            return []
    
    def save_schedules(self, schedules: List[ChannelSchedule]) -> bool:
        """Zapisuje harmonogramy do pliku"""
        try:
            data = {
                "channels": [schedule.to_dict() for schedule in schedules]
            }
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False
    
    def add_schedule(self, schedule: ChannelSchedule) -> bool:
        """Dodaje nowy harmonogram"""
        schedules = self.load_schedules()
        
        # Sprawdź czy kanał już istnieje
        if any(s.channel_id == schedule.channel_id for s in schedules):
            return False
        
        schedules.append(schedule)
        return self.save_schedules(schedules)
    
    def remove_schedule(self, channel_id: int) -> bool:
        """Usuwa harmonogram dla danego kanału"""
        schedules = self.load_schedules()
        initial_count = len(schedules)
        
        schedules = [s for s in schedules if s.channel_id != channel_id]
        
        if len(schedules) < initial_count:
            return self.save_schedules(schedules)
        return False
    
    def get_schedule(self, channel_id: int) -> Optional[ChannelSchedule]:
        """Pobiera harmonogram dla danego kanału"""
        schedules = self.load_schedules()
        for schedule in schedules:
            if schedule.channel_id == channel_id:
                return schedule
        return None
