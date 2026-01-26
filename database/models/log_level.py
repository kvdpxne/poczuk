from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.base import Base

# if TYPE_CHECKING:
#     from database.models.log import Log


class LogLevel(Base):
    __tablename__ = "log_levels"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)

    # Relacje