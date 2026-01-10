"""
Zarządzanie harmonogramami - Single Responsibility Principle
"""
import asyncio
from datetime import datetime
from typing import List
from models.channel_schedule import ChannelSchedule
from utils.validators import TimeValidator
from services.channel_cleaner import ChannelCleaner
from utils.logger import get_logger


class Scheduler:
    """Zarządza harmonogramem czyszczenia kanałów"""

    def __init__(self, bot, config_manager):
        self.bot = bot
        self.config_manager = config_manager
        self.cleaner = ChannelCleaner()
        self.validator = TimeValidator()
        self.logger = get_logger(__name__)

    async def start(self):
        """Uruchamia proces sprawdzania harmonogramu"""
        await self.bot.wait_until_ready()

        self.logger.info("Rozpoczęto monitorowanie harmonogramów")

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
        try:
            self.logger.info(
                f"Wykonuję harmonogram: kanał={schedule.channel_name} ({schedule.channel_id}), "
                f"czas={schedule.time}, potwierdzenie={'TAK' if schedule.send_confirmation else 'NIE'}"
            )

            # Przekaż informację o potwierdzeniu do cleanera
            deleted_count = await self.cleaner.clean_channel(
                self.bot,
                schedule.channel_id,
                send_confirmation=schedule.send_confirmation
            )

            # Zaloguj wykonanie
            # log_schedule_execution(schedule.channel_id, schedule.channel_name, deleted_count)

        except Exception as e:
            self.logger.error(
                f"Błąd wykonania harmonogramu: kanał={schedule.channel_id}, błąd={e}",
                exc_info=True
            )

    async def execute_test_clean(self, channel_id: int) -> int:
        """Wykonuje testowe czyszczenie (bez harmonogramu)"""
        print(f"\n[{datetime.now()}] Testowe czyszczenie dla {channel_id}")
        return await self.cleaner.clean_channel(self.bot, channel_id)

    def get_all_schedules(self) -> List[ChannelSchedule]:
        """Zwraca wszystkie harmonogramy"""
        return self.config_manager.load_schedules()