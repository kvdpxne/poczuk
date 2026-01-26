from datetime import datetime
from decimal import Decimal
from typing import Optional, TYPE_CHECKING

from sqlalchemy import Integer, Boolean, DateTime, func, DECIMAL, Text, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base

if TYPE_CHECKING:
    from database.models.debt_schedule import DebtSchedule


class Debt(Base):
    __tablename__ = "debts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    debtor_id: Mapped[int] = mapped_column(Integer, nullable=False)
    creditor_id: Mapped[int] = mapped_column(Integer, nullable=False)
    amount: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="PLN")
    description: Mapped[Optional[str]] = mapped_column(Text)
    guild_id: Mapped[int] = mapped_column(Integer, nullable=False)
    is_settled: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now()
    )

    # Relacje
    reminders: Mapped[list["DebtSchedule"]] = relationship(
        "DebtSchedule",
        back_populates="debt",
        cascade="all, delete-orphan"
    )