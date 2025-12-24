"""
Zarządzanie harmonogramami
"""
import asyncio
from datetime import datetime
from typing import List
from models.channel_schedule import ChannelSchedule
from utils.validators import TimeValidator
from services.channel_cleaner import ChannelCleaner


class Scheduler:
    """Zarządza harmonogramem czyszczenia kanałów"""
    
    def __init__(self, bot, config_manager):
        self.bot = bot
        self.config_manager = config_manager
        self.cleaner = ChannelCleaner()
        self.validator = TimeValidator()
    
    async def start(self):
        """Uruchamia proces sprawdzania harmonogramu"""
        await self.bot.wait_until_ready()
        
        while not self.bot.is_closed():
            await self._check_and_execute_schedules()
            await asyncio.sleep(60)  # Sprawdzaj co minutę
    
    async def _check_and_execute_schedules(self):
        """Sprawdza i wykonuje harmonogramy"""
        current_time = self.validator.get_current_time()
        schedules = self.config_manager.load_schedules()
        
        for schedule in schedules:
            if schedule.matches_current_time(current_time):
                await self._execute_schedule(schedule)
    
    async def _execute_schedule(self, schedule: ChannelSchedule):
        """Wykonuje czyszczenie dla danego harmonogramu"""
        print(f"\n[{datetime.now()}] Wykonuję harmonogram dla {schedule.channel_id}")
        await self.cleaner.clean_channel(self.bot, schedule.channel_id)
    
    async def execute_test_clean(self, channel_id: int) -> int:
        """Wykonuje testowe czyszczenie (bez harmonogramu)"""
        print(f"\n[{datetime.now()}] Testowe czyszczenie dla {channel_id}")
        return await self.cleaner.clean_channel(self.bot, channel_id)
    
    def get_all_schedules(self) -> List[ChannelSchedule]:
        """Zwraca wszystkie harmonogramy"""
        return self.config_manager.load_schedules()
