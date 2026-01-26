from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Integer, ForeignKey, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base

if TYPE_CHECKING:
    from database.models.action_type import ActionType
    from database.models.log_level import LogLevel


class Log(Base):
    __tablename__ = "logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    guild_id: Mapped[int] = mapped_column(Integer, nullable=False)
    log_level_id: Mapped[int] = mapped_column(ForeignKey("log_levels.id"), nullable=False)
    action_type_id: Mapped[int] = mapped_column(ForeignKey("action_types.id"), nullable=False)
    details: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Relacje - używamy stringów z pełnymi ścieżkami
    log_level: Mapped["LogLevel"] = relationship("LogLevel")
    action_type: Mapped["ActionType"] = relationship("ActionType")
