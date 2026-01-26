from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base

if TYPE_CHECKING:
    from database.models.debt import Debt
    from database.models.schedule import Schedule


class DebtSchedule(Base):
    __tablename__ = "debt_schedules"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    debt_id: Mapped[int] = mapped_column(ForeignKey("debts.id"), nullable=False)
    schedule_id: Mapped[int] = mapped_column(ForeignKey("schedules.id"), nullable=False)
    last_reminded_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Relacje
    debt: Mapped["Debt"] = relationship("Debt", back_populates="reminders")
    schedule: Mapped["Schedule"] = relationship("Schedule", back_populates="debt_reminders")
