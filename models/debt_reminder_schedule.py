"""
Model danych dla harmonogramu przypomnień o długach - Single Responsibility Principle
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class DebtReminderSchedule:
    """Model reprezentujący harmonogram przypomnień o długach"""
    guild_id: int
    channel_id: int
    run_time: str
    frequency_id: int
    message_template: Optional[str] = None
    is_active: bool = True
    added_by: Optional[int] = None
    added_at: Optional[datetime] = None
    last_run_at: Optional[datetime] = None
    schedule_id: Optional[int] = None

    def __post_init__(self):
        if self.added_at is None:
            from datetime import datetime
            self.added_at = datetime.now()
        if self.message_template is None:
            self.message_template = (
                "Przypomnienie o długu: {debtor} jest winien {creditor} "
                "kwotę {amount} {currency}. Opis: {description}"
            )

    def format_message(self, debtor_name: str, creditor_name: str,
                       amount: str, currency: str, description: str = "") -> str:
        """Formatuje wiadomość przypomnienia"""
        return self.message_template.format(
            debtor=debtor_name,
            creditor=creditor_name,
            amount=amount,
            currency=currency,
            description=description or "brak opisu"
        )