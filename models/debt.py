"""
Model danych dla długu - Single Responsibility Principle
"""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass
class Debt:
    """Model reprezentujący dług między użytkownikami"""
    debtor_id: int
    creditor_id: int
    amount: Decimal
    description: Optional[str] = None
    guild_id: Optional[int] = None
    currency: str = "PLN"
    is_settled: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    debt_id: Optional[int] = None
    schedule_ids: list[int] = None  # Lista harmonogramów przypomnień

    def __post_init__(self):
        if self.schedule_ids is None:
            self.schedule_ids = []
        if self.created_at is None:
            from datetime import datetime
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = self.created_at

    def to_dict(self) -> dict:
        """Konwertuje obiekt do słownika"""
        return {
            "debtor_id": self.debtor_id,
            "creditor_id": self.creditor_id,
            "amount": str(self.amount),
            "description": self.description,
            "guild_id": self.guild_id,
            "currency": self.currency,
            "is_settled": self.is_settled,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "debt_id": self.debt_id,
            "schedule_ids": self.schedule_ids
        }