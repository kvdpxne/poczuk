from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base

if TYPE_CHECKING:
    from database.models.schedule import Schedule


class Frequency(Base):
    __tablename__ = "frequencies"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)

    # Relacje
    schedules: Mapped[list["Schedule"]] = relationship(
        "Schedule",
        back_populates="frequency",
        cascade="all, delete-orphan"
    )
