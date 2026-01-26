from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class GuildSetting(Base):
    __tablename__ = "guild_settings"

    guild_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key: Mapped[str] = mapped_column(String(50), primary_key=True)
    value: Mapped[str] = mapped_column(String(255))
