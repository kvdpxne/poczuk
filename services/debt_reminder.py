"""
Serwis wysyłania przypomnień o długach - Single Responsibility Principle
"""
import discord
from models.debt_reminder_schedule import DebtReminderSchedule
from utils.helpers import create_embed
from utils.logger import get_logger


class DebtReminder:
    """Odpowiedzialny za wysyłanie przypomnień o długach"""

    def __init__(self, bot, config_manager):
        self.bot = bot
        self.config_manager = config_manager
        self.logger = get_logger(__name__)

    async def send_reminders(self, schedule: DebtReminderSchedule):
        """Wysyła przypomnienia o długach zgodnie z harmonogramem"""
        try:
            channel = self.bot.get_channel(schedule.channel_id)
            if not channel:
                self.logger.error(f"Nie znaleziono kanału: {schedule.channel_id}")
                return

            # Pobierz wszystkie niezapłacone długi na serwerze
            debts = self.config_manager.get_debts(
                guild_id=schedule.guild_id,
                is_settled=False
            )

            if not debts:
                self.logger.info(f"Brak długów do przypomnienia na kanale {channel.id}")
                return

            # Podziel długi na grupy dla czytelności
            debt_groups = {}
            for debt in debts:
                key = (debt.debtor_id, debt.creditor_id)
                if key not in debt_groups:
                    debt_groups[key] = []
                debt_groups[key].append(debt)

            # Wyślij przypomnienia
            for (debtor_id, creditor_id), debt_list in list(debt_groups.items())[:10]:  # Ogranicz do 10 przypomnień
                total_amount = sum(debt.amount for debt in debt_list)

                # Pobierz dane użytkowników
                debtor = channel.guild.get_member(debtor_id)
                creditor = channel.guild.get_member(creditor_id)

                if not debtor or not creditor:
                    continue

                # Formatuj wiadomość
                message = schedule.format_message(
                    debtor_name=debtor.display_name,
                    creditor_name=creditor.display_name,
                    amount=str(total_amount),
                    currency=debt_list[0].currency,
                    description=", ".join(d.description for d in debt_list if d.description)
                )

                # Wyślij jako embed dla lepszego wyglądu
                embed = create_embed(
                    title="💰 Przypomnienie o długu",
                    description=message,
                    color=discord.Color.orange()
                )
                embed.add_field(name="Dłużnik", value=debtor.mention, inline=True)
                embed.add_field(name="Wierzyciel", value=creditor.mention, inline=True)
                embed.add_field(name="Łączna kwota", value=f"{total_amount} {debt_list[0].currency}", inline=True)
                embed.set_footer(text="Przypomnienie automatyczne")

                await channel.send(embed=embed)
                self.logger.info(f"Wysłano przypomnienie: {debtor_id} → {creditor_id}: {total_amount}")

        except Exception as e:
            self.logger.error(f"Błąd wysyłania przypomnień: {e}", exc_info=True)