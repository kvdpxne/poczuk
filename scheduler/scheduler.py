"""
Zarządzanie harmonogramami - Single Responsibility Principle
"""
import asyncio
from datetime import datetime
from typing import List
from models.cleaning_schedule import CleaningSchedule
from models.debt_reminder_schedule import DebtReminderSchedule
from utils.validators import TimeValidator
from services.channel_cleaner import ChannelCleaner
from services.debt_reminder import DebtReminder
from utils.logger import get_logger


class Scheduler:
    """Zarządza harmonogramami różnych zadań"""

    def __init__(self, bot, config_manager):
        self.bot = bot
        self.config_manager = config_manager
        self.cleaner = ChannelCleaner()
        self.debt_reminder = DebtReminder(bot, config_manager)
        self.validator = TimeValidator()
        self.logger = get_logger(__name__)

    async def start(self):
        """Uruchamia proces sprawdzania harmonogramów"""
        await self.bot.wait_until_ready()

        self.logger.info("Rozpoczęto monitorowanie harmonogramów")

        while not self.bot.is_closed():
            await self._check_and_execute_schedules()
            await asyncio.sleep(60)  # Sprawdzaj co minutę

    async def _check_and_execute_schedules(self):
        """Sprawdza i wykonuje harmonogramy"""
        current_time = self.validator.get_current_time()

        # Sprawdź harmonogramy czyszczenia
        cleaning_schedules = self.config_manager.get_all_cleaning_schedules()
        for schedule in cleaning_schedules:
            if schedule.matches_current_time(current_time):
                await self._execute_cleaning_schedule(schedule)

        # Sprawdź harmonogramy przypomnień o długach
        reminder_schedules = self.config_manager.get_debt_reminder_schedules()
        for schedule in reminder_schedules:
            if schedule.is_active and schedule.run_time == current_time:
                await self._execute_debt_reminder_schedule(schedule)

    async def _execute_cleaning_schedule(self, schedule: CleaningSchedule):
        """Wykonuje czyszczenie dla danego harmonogramu"""
        try:
            self.logger.info(
                f"Wykonuję harmonogram czyszczenia: kanał={schedule.channel_id}, "
                f"czas={schedule.time}"
            )

            # Wykonaj czyszczenie
            deleted_count = await self.cleaner.clean_channel(
                self.bot,
                schedule.channel_id,
                exclude_pinned=schedule.exclude_pinned
            )

            # Aktualizuj czas ostatniego uruchomienia
            if schedule.schedule_id:
                self.config_manager.update_cleaning_schedule_last_run(
                    schedule.schedule_id,
                    datetime.now()
                )

            # Zaloguj akcję
            self.config_manager.add_log(
                user_id=self.bot.user.id,
                guild_id=schedule.guild_id,
                log_level_name="INFO",
                action_type_name="RUN_CLEANING",
                details=f"Wykonano czyszczenie: kanał={schedule.channel_id}, usunięto={deleted_count}"
            )

            self.logger.info(
                f"Zakończono harmonogram czyszczenia: kanał={schedule.channel_id}, "
                f"usunięto={deleted_count} wiadomości"
            )

        except Exception as e:
            self.logger.error(
                f"Błąd wykonania harmonogramu czyszczenia: kanał={schedule.channel_id}, błąd={e}",
                exc_info=True
            )

    async def _execute_debt_reminder_schedule(self, schedule: DebtReminderSchedule):
        """Wykonuje przypomnienia o długach"""
        try:
            self.logger.info(
                f"Wykonuję harmonogram przypomnień: kanał={schedule.channel_id}, "
                f"czas={schedule.run_time}"
            )

            await self.debt_reminder.send_reminders(schedule)

            # Zaloguj akcję
            self.config_manager.add_log(
                user_id=self.bot.user.id,
                guild_id=schedule.guild_id,
                log_level_name="INFO",
                action_type_name="SEND_REMINDER",
                details=f"Wysłano przypomnienia o długach: kanał={schedule.channel_id}"
            )

        except Exception as e:
            self.logger.error(
                f"Błąd wykonania harmonogramu przypomnień: kanał={schedule.channel_id}, błąd={e}",
                exc_info=True
            )