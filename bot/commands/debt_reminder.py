import discord

from models.debt_reminder_schedule import DebtReminderSchedule
from utils import get_logger
from utils.helpers import create_embed


class ReminderDebtCommand:

    def __init__(self, bot, config_manager, validator, logger=None):
        self.bot = bot
        self.validator = validator
        self.config_manager = config_manager
        self.logger = logger or get_logger(__name__)

    async def handle(self, ctx, channel: discord.TextChannel, run_time: str,
                                       frequency_id: int = 1, message_template: str = ""):
        """Dodaje harmonogram przypomnień o długach"""
        try:
            # Walidacja czasu
            if not self.validator.validate_time_format(run_time):
                return await ctx.send("❌ Nieprawidłowy format czasu. Użyj HH:MM (np. 09:00)")

            # Stwórz harmonogram
            schedule = DebtReminderSchedule(
                guild_id=ctx.guild.id,
                channel_id=channel.id,
                run_time=run_time,
                frequency_id=frequency_id,
                message_template=message_template,
                added_by=ctx.author.id
            )

            if self.config_manager.add_debt_reminder_schedule(schedule):
                # Zaloguj akcję
                self.config_manager.add_log(
                    user_id=ctx.author.id,
                    guild_id=ctx.guild.id,
                    log_level_name="INFO",
                    action_type_name="ADD_SCHEDULE",
                    details=f"Dodano harmonogram przypomnień: {channel.name} ({channel.id}) o {run_time}"
                )

                embed = create_embed(
                    title="✅ Harmonogram przypomnień dodany",
                    description=f"Przypomnienia o długach będą wysyłane na {channel.mention} o **{run_time}**",
                    color=discord.Color.green()
                )
                embed.add_field(name="Częstotliwość",
                                value="Codziennie" if frequency_id == 1 else "Co tydzień",
                                inline=True)
                await ctx.send(embed=embed)
            else:
                await ctx.send("❌ Nie udało się dodać harmonogramu przypomnień")

        except Exception as e:
            self.logger.error(f"Błąd dodawania harmonogramu przypomnień: {e}", exc_info=True)
            await ctx.send("❌ Wystąpił błąd podczas dodawania harmonogramu")