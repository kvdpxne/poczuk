from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, func, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base

if TYPE_CHECKING:
    from database.models.debt_schedule import DebtSchedule
    from database.models.frequency import Frequency


class Schedule(Base):
    __tablename__ = "schedules"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    task_type: Mapped[str] = mapped_column(String(20), default="cleaning")

    # Wspólne pola dla wszystkich typów zadań
    guild_id: Mapped[int] = mapped_column(Integer, nullable=False)
    channel_id: Mapped[int] = mapped_column(Integer, nullable=False)
    run_time: Mapped[str] = mapped_column(String(5), nullable=False)  # HH:MM
    frequency_id: Mapped[int] = mapped_column(
        ForeignKey("frequencies.id"),
        nullable=False,
        default=1  # Domyślnie daily
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    added_by: Mapped[int] = mapped_column(Integer, nullable=False)
    added_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    last_run_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Pola specyficzne dla czyszczenia
    exclude_pinned: Mapped[bool] = mapped_column(Boolean, default=True)

    # Pola specyficzne dla przypomnień o długach
    message_template: Mapped[Optional[str]] = mapped_column(Text)

    # Relacje
    frequency: Mapped["Frequency"] = relationship("Frequency", back_populates="schedules")
    debt_reminders: Mapped[list["DebtSchedule"]] = relationship(
        "DebtSchedule",
        back_populates="schedule",
        cascade="all, delete-orphan"
    )

    def to_cleaning_domain(self):
        """Konwertuje do modelu domenowego czyszczenia"""
        from models.cleaning_schedule import CleaningSchedule
        return CleaningSchedule(
            channel_id=self.channel_id,
            channel_name="",  # Musi być uzupełniane
            time=self.run_time,
            guild_id=self.guild_id,
            frequency_id=self.frequency_id,
            is_active=self.is_active,
            exclude_pinned=self.exclude_pinned,
            added_by=self.added_by,
            added_at=self.added_at,
            last_run_at=self.last_run_at,
            schedule_id=self.id
        )
