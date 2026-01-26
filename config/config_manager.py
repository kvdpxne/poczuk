import os
from datetime import datetime
from typing import List, Optional, Any

from sqlalchemy import create_engine, select, delete, update, and_
from sqlalchemy.orm import Session

from database.base import Base
from database.models.action_type import ActionType
from database.models.debt import Debt
from database.models.debt_schedule import DebtSchedule
from database.models.frequency import Frequency
from database.models.guild_setting import GuildSetting
from database.models.log import Log
from database.models.log_level import LogLevel
from database.models.schedule import Schedule
from database.models.user_setting import UserSetting
from models.channel_schedule import ChannelSchedule
from models.cleaning_schedule import CleaningSchedule
from models.debt import Debt as DebtModel
from models.debt_reminder_schedule import DebtReminderSchedule
from utils.logger import get_logger


class ConfigManager:
    """Zarządza konfiguracją bota - Single Responsibility Principle"""

    def __init__(self, db_path: str = "data/bot_database.db"):
        self.db_path = db_path
        self.logger = get_logger(__name__)
        self._ensure_data_directory()
        self.engine = create_engine(f"sqlite:///{self.db_path}")
        self._create_tables()
        self._seed_default_data()

    def _ensure_data_directory(self):
        """Tworzy katalog danych jeśli nie istnieje"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def _create_tables(self):
        """Tworzy tabele w bazie danych"""
        Base.metadata.create_all(self.engine)

    def _seed_default_data(self):
        """Wypełnia domyślne dane w tabelach referencyjnych"""
        with Session(self.engine) as session:
            # Domyślne częstotliwości
            frequencies = session.scalars(select(Frequency)).all()
            if not frequencies:
                default_frequencies = [
                    Frequency(name="daily", description="Codziennie"),
                    Frequency(name="weekly", description="Co tydzień"),
                    Frequency(name="interval", description="Co określony interwał"),
                ]
                session.add_all(default_frequencies)

            # Domyślne typy akcji
            action_types = session.scalars(select(ActionType)).all()
            if not action_types:
                default_action_types = [
                    ActionType(name="ADD_SCHEDULE", description="Dodanie harmonogramu"),
                    ActionType(name="DELETE_SCHEDULE", description="Usunięcie harmonogramu"),
                    ActionType(name="UPDATE_SETTING", description="Aktualizacja ustawienia"),
                    ActionType(name="ADD_DEBT", description="Dodanie długu"),
                    ActionType(name="SETTLE_DEBT", description="Spłata długu"),
                    ActionType(name="RUN_CLEANING", description="Wykonanie czyszczenia"),
                    ActionType(name="SEND_REMINDER", description="Wysłanie przypomnienia"),
                ]
                session.add_all(default_action_types)

            # Domyślne poziomy logowania
            log_levels = session.scalars(select(LogLevel)).all()
            if not log_levels:
                default_log_levels = [
                    LogLevel(name="INFO", description="Informacja"),
                    LogLevel(name="WARN", description="Ostrzeżenie"),
                    LogLevel(name="ERROR", description="Błąd"),
                    LogLevel(name="DEBUG", description="Debug"),
                ]
                session.add_all(default_log_levels)

            session.commit()

    # --- Zarządzanie logami ---

    def add_log(self, user_id: int, guild_id: int, log_level_name: str,
                action_type_name: str, details: str) -> bool:
        """Dodaje wpis do logów"""
        try:
            with Session(self.engine) as session:
                # Znajdź ID poziomu logowania
                log_level = session.scalar(
                    select(LogLevel).where(LogLevel.name == log_level_name)
                )
                if not log_level:
                    self.logger.error(f"Nieznany poziom logowania: {log_level_name}")
                    return False

                # Znajdź ID typu akcji
                action_type = session.scalar(
                    select(ActionType).where(ActionType.name == action_type_name)
                )
                if not action_type:
                    self.logger.error(f"Nieznany typ akcji: {action_type_name}")
                    return False

                # Dodaj log
                log = Log(
                    user_id=user_id,
                    guild_id=guild_id,
                    log_level_id=log_level.id,
                    action_type_id=action_type.id,
                    details=details
                )
                session.add(log)
                session.commit()
                return True
        except Exception as e:
            self.logger.error(f"Błąd dodawania logu: {e}")
            return False

    # --- Harmonogramy czyszczenia ---

    def add_cleaning_schedule(self, schedule: CleaningSchedule) -> bool:
        """Dodaje harmonogram czyszczenia"""
        try:
            with Session(self.engine) as session:
                schedule_db = Schedule(
                    task_type="cleaning",
                    guild_id=schedule.guild_id,
                    channel_id=schedule.channel_id,
                    run_time=schedule.time,
                    frequency_id=schedule.frequency_id,
                    is_active=schedule.is_active,
                    added_by=schedule.added_by,
                    added_at=schedule.added_at,
                    last_run_at=schedule.last_run_at,
                    exclude_pinned=schedule.exclude_pinned,
                    message_template=None
                )
                session.add(schedule_db)
                session.commit()
                schedule.schedule_id = schedule_db.id
                return True
        except Exception as e:
            self.logger.error(f"Błąd dodawania harmonogramu czyszczenia {schedule.channel_id}: {e}")
            return False

    def update_cleaning_schedule_last_run(self, schedule_id: int, last_run_at: datetime) -> bool:
        """Aktualizuje czas ostatniego uruchomienia harmonogramu"""
        try:
            with Session(self.engine) as session:
                stmt = update(Schedule).where(
                    Schedule.id == schedule_id
                ).values(last_run_at=last_run_at)
                session.execute(stmt)
                session.commit()
                return True
        except Exception as e:
            self.logger.error(f"Błąd aktualizacji harmonogramu {schedule_id}: {e}")
            return False

    def remove_cleaning_schedule(self, channel_id: int, guild_id: int) -> bool:
        """Usuwa harmonogram czyszczenia"""
        try:
            with Session(self.engine) as session:
                stmt = delete(Schedule).where(
                    and_(
                        Schedule.channel_id == channel_id,
                        Schedule.guild_id == guild_id,
                        Schedule.task_type == "cleaning"
                    )
                )
                result = session.execute(stmt)
                session.commit()
                return result.rowcount > 0
        except Exception as e:
            self.logger.error(f"Błąd usuwania harmonogramu {channel_id}: {e}")
            return False

    def get_cleaning_schedule(self, channel_id: int, guild_id: int) -> Optional[CleaningSchedule]:
        """Pobiera harmonogram czyszczenia"""
        try:
            with Session(self.engine) as session:
                stmt = select(Schedule).where(
                    and_(
                        Schedule.channel_id == channel_id,
                        Schedule.guild_id == guild_id,
                        Schedule.task_type == "cleaning"
                    )
                )
                result = session.scalar(stmt)
                if result:
                    domain_schedule = result.to_cleaning_domain()
                    domain_schedule.schedule_id = result.id
                    return domain_schedule
                return None
        except Exception as e:
            self.logger.error(f"Błąd pobierania harmonogramu {channel_id}: {e}")
            return None

    def get_all_cleaning_schedules(self) -> List[CleaningSchedule]:
        """Pobiera wszystkie harmonogramy czyszczenia"""
        try:
            with Session(self.engine) as session:
                stmt = select(Schedule).where(
                    Schedule.task_type == "cleaning"
                )
                results = session.scalars(stmt).all()
                schedules = []
                for result in results:
                    domain_schedule = result.to_cleaning_domain()
                    domain_schedule.schedule_id = result.id
                    schedules.append(domain_schedule)
                return schedules
        except Exception as e:
            self.logger.error(f"Błąd ładowania harmonogramów czyszczenia: {e}")
            return []

    # --- Zarządzanie długami ---

    def add_debt(self, debt: DebtModel) -> bool:
        """Dodaje nowy dług"""
        try:
            with Session(self.engine) as session:
                debt_db = Debt(
                    debtor_id=debt.debtor_id,
                    creditor_id=debt.creditor_id,
                    amount=debt.amount,
                    currency=debt.currency,
                    description=debt.description,
                    guild_id=debt.guild_id,
                    is_settled=debt.is_settled,
                    created_at=debt.created_at,
                    updated_at=debt.updated_at
                )
                session.add(debt_db)
                session.commit()
                debt.debt_id = debt_db.id

                # Dodaj powiązania z harmonogramami przypomnień
                for schedule_id in debt.schedule_ids:
                    debt_schedule = DebtSchedule(
                        debt_id=debt_db.id,
                        schedule_id=schedule_id
                    )
                    session.add(debt_schedule)

                session.commit()
                return True
        except Exception as e:
            self.logger.error(f"Błąd dodawania długu: {e}")
            return False

    def settle_debt(self, debt_id: int) -> bool:
        """Oznacza dług jako spłacony"""
        try:
            with Session(self.engine) as session:
                stmt = update(Debt).where(
                    Debt.id == debt_id
                ).values(is_settled=True, updated_at=datetime.now())
                result = session.execute(stmt)
                session.commit()
                return result.rowcount > 0
        except Exception as e:
            self.logger.error(f"Błąd oznaczania długu jako spłacony {debt_id}: {e}")
            return False

    def get_debts(self, guild_id: int, debtor_id: Optional[int] = None,
                  creditor_id: Optional[int] = None, is_settled: Optional[bool] = None) -> List[DebtModel]:
        """Pobiera długi według kryteriów"""
        try:
            with Session(self.engine) as session:
                conditions = [Debt.guild_id == guild_id]

                if debtor_id is not None:
                    conditions.append(Debt.debtor_id == debtor_id)

                if creditor_id is not None:
                    conditions.append(Debt.creditor_id == creditor_id)

                if is_settled is not None:
                    conditions.append(Debt.is_settled == is_settled)

                stmt = select(Debt).where(and_(*conditions))
                results = session.scalars(stmt).all()

                debts = []
                for result in results:
                    debt = DebtModel(
                        debtor_id=result.debtor_id,
                        creditor_id=result.creditor_id,
                        amount=result.amount,
                        currency=result.currency,
                        description=result.description,
                        guild_id=result.guild_id,
                        is_settled=result.is_settled,
                        created_at=result.created_at,
                        updated_at=result.updated_at,
                        debt_id=result.id
                    )

                    # Pobierz powiązane harmonogramy
                    schedule_stmt = select(DebtSchedule).where(
                        DebtSchedule.debt_id == result.id
                    )
                    schedule_results = session.scalars(schedule_stmt).all()
                    debt.schedule_ids = [ds.schedule_id for ds in schedule_results]

                    debts.append(debt)

                return debts
        except Exception as e:
            self.logger.error(f"Błąd pobierania długów: {e}")
            return []

    # --- Harmonogramy przypomnień o długach ---

    def add_debt_reminder_schedule(self, schedule: DebtReminderSchedule) -> bool:
        """Dodaje harmonogram przypomnień o długach"""
        try:
            with Session(self.engine) as session:
                schedule_db = Schedule(
                    task_type="debt_reminder",
                    guild_id=schedule.guild_id,
                    channel_id=schedule.channel_id,
                    run_time=schedule.run_time,
                    frequency_id=schedule.frequency_id,
                    is_active=schedule.is_active,
                    added_by=schedule.added_by,
                    added_at=schedule.added_at,
                    last_run_at=schedule.last_run_at,
                    exclude_pinned=False,
                    message_template=schedule.message_template
                )
                session.add(schedule_db)
                session.commit()
                schedule.schedule_id = schedule_db.id
                return True
        except Exception as e:
            self.logger.error(f"Błąd dodawania harmonogramu przypomnień: {e}")
            return False

    def get_debt_reminder_schedules(self, guild_id: Optional[int] = None) -> List[DebtReminderSchedule]:
        """Pobiera harmonogramy przypomnień o długach"""
        try:
            with Session(self.engine) as session:
                conditions = [Schedule.task_type == "debt_reminder"]
                if guild_id is not None:
                    conditions.append(Schedule.guild_id == guild_id)

                stmt = select(Schedule).where(and_(*conditions))
                results = session.scalars(stmt).all()

                schedules = []
                for result in results:
                    schedule = DebtReminderSchedule(
                        guild_id=result.guild_id,
                        channel_id=result.channel_id,
                        run_time=result.run_time,
                        frequency_id=result.frequency_id,
                        message_template=result.message_template,
                        is_active=result.is_active,
                        added_by=result.added_by,
                        added_at=result.added_at,
                        last_run_at=result.last_run_at,
                        schedule_id=result.id
                    )
                    schedules.append(schedule)

                return schedules
        except Exception as e:
            self.logger.error(f"Błąd pobierania harmonogramów przypomnień: {e}")
            return []

    # --- Ustawienia serwera (guild settings) ---
    def set_guild_setting(self, guild_id: int, key: str, value: str) -> bool:
        """Ustawia wartość dla serwera"""
        try:
            with Session(self.engine) as session:
                setting = GuildSetting(
                    guild_id=guild_id,
                    key=key,
                    value=str(value)
                )
                session.merge(setting)
                session.commit()
                return True
        except Exception as e:
            self.logger.error(f"Błąd zapisu ustawień gildii {guild_id}.{key}: {e}")
            return False

    def get_guild_setting(self, guild_id: int, key: str, default: Any = None) -> str:
        """Pobiera wartość ustawienia serwera"""
        try:
            with Session(self.engine) as session:
                stmt = select(GuildSetting).where(
                    GuildSetting.guild_id == guild_id,
                    GuildSetting.key == key
                )
                result = session.scalar(stmt)
                return result.value if result else default
        except Exception:
            return default

    # --- Ustawienia użytkownika (user settings) ---
    def set_user_setting(self, user_id: int, key: str, value: str) -> bool:
        """Ustawia wartość dla użytkownika"""
        try:
            with Session(self.engine) as session:
                setting = UserSetting(
                    user_id=user_id,
                    key=key,
                    value=str(value)
                )
                session.merge(setting)
                session.commit()
                return True
        except Exception as e:
            self.logger.error(f"Błąd zapisu ustawień użytkownika {user_id}.{key}: {e}")
            return False

    def get_user_setting(self, user_id: int, key: str, default: Any = None) -> str:
        """Pobiera wartość ustawienia użytkownika"""
        try:
            with Session(self.engine) as session:
                stmt = select(UserSetting).where(
                    UserSetting.user_id == user_id,
                    UserSetting.key == key
                )
                result = session.scalar(stmt)
                return result.value if result else default
        except Exception:
            return default

    def load_schedules(self) -> List[ChannelSchedule]:
        """Pobiera wszystkie harmonogramy"""
        try:
            with Session(self.engine) as session:
                stmt = select(Schedule)
                results = session.scalars(stmt).all()
                return [r.to_domain() for r in results]
        except Exception as e:
            self.logger.error(f"Błąd ładowania listy harmonogramów: {e}")
            return []
