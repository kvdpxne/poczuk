from decimal import Decimal

import discord

from bot.commands import AvatarCommand, CoinFlipCommand, UptimeCommand, SetNicknameCommand, HelpCommand, VersionCommand, \
    WhoisCommand, InfoCommand, PurgeCommand, SourceCodeCommand, CleanCommand
from bot.commands.debt_add import AddDebtCommand
from bot.commands.debt_list import ListDebtCommand
from bot.commands.debt_reminder import ReminderDebtCommand
from bot.commands.debt_settle import SettleDebtCommand
from bot.commands.delete_nickname import DeleteNicknameCommand
from bot.commands.ping import PingCommand
from models.cleaning_schedule import CleaningSchedule
from utils.helpers import create_embed, get_current_datetime
from utils.logger import get_logger
from utils.validators import TimeValidator


class CommandHandler:

    def __init__(self, bot, config_manager, scheduler):
        self.bot = bot
        self.config_manager = config_manager
        self.scheduler = scheduler
        self.validator = TimeValidator()
        self.logger = get_logger(__name__)

        self.debt_add = AddDebtCommand(bot, config_manager, self.logger)
        self.debt_list = ListDebtCommand(bot, config_manager, self.logger)
        self.debt_reminder = ReminderDebtCommand(bot, config_manager, self.validator, self.logger)
        self.debt_settle = SettleDebtCommand(bot, config_manager, self.logger)

        # Inicjalizacja modułów komend
        self.avatar_command = AvatarCommand(bot, self.logger)
        self.coinflip_command = CoinFlipCommand(bot, self.logger)
        self.delete_nickname = DeleteNicknameCommand(bot, self.logger)
        self.help_command = HelpCommand(bot, self.logger)
        self.ping_command = PingCommand(bot, self.logger)
        self.set_nickname_command = SetNicknameCommand(bot, self.logger)
        self.uptime_command = UptimeCommand(bot, self.logger)
        self.version_command = VersionCommand(bot, self.logger)
        self.whois_command = WhoisCommand(bot, self.logger)
        self.info_command = InfoCommand(bot, config_manager, self.logger)
        self.purge_command = PurgeCommand(bot, self.logger)
        self.source_code_command = SourceCodeCommand(bot, self.logger)
        self.clean_command = CleanCommand(bot, self.logger)

    async def handle_add(self, ctx, channel: discord.TextChannel, clean_time: str, options: str = ""):
        """Obsługuje komendę !add z opcjonalnymi flagami (czyszczenie)"""
        try:
            # Walidacja czasu
            if not self.validator.validate_time_format(clean_time):
                self.logger.warning(f"Nieprawidłowy format czasu: {clean_time} od {ctx.author}")
                return await ctx.send("❌ Nieprawidłowy format czasu. Użyj HH:MM (np. 03:00)")

            # Sprawdź czy kanał już ma harmonogram
            existing = self.config_manager.get_cleaning_schedule(channel.id, ctx.guild.id)
            if existing:
                self.logger.info(f"Próba dodania istniejącego harmonogramu: {channel.id} od {ctx.author}")
                return await ctx.send(
                    f"❌ Kanał {channel.mention} już ma ustawione czyszczenie o {existing.time}"
                )

            # Przetwarzanie opcji (flag)
            exclude_pinned = True
            frequency_id = 1  # Domyślnie codziennie

            # Parsowanie flag
            options_lower = options.lower()
            if "--include-pinned" in options_lower:
                exclude_pinned = False
            if "--weekly" in options_lower:
                frequency_id = 2  # weekly

            # Utwórz nowy harmonogram czyszczenia
            new_schedule = CleaningSchedule(
                channel_id=channel.id,
                channel_name=channel.name,
                time=clean_time,
                added_by=ctx.author.id,
                added_at=get_current_datetime(),
                guild_id=ctx.guild.id,
                frequency_id=frequency_id,
                exclude_pinned=exclude_pinned
            )

            # Zapisz harmonogram
            if self.config_manager.add_cleaning_schedule(new_schedule):
                # Zaloguj akcję
                self.config_manager.add_log(
                    user_id=ctx.author.id,
                    guild_id=ctx.guild.id,
                    log_level_name="INFO",
                    action_type_name="ADD_SCHEDULE",
                    details=f"Dodano harmonogram czyszczenia: {channel.name} ({channel.id}) o {clean_time}"
                )

                self.logger.info(
                    f"Dodano harmonogram czyszczenia: kanał={channel.name} ({channel.id}), "
                    f"czas={clean_time}, częstotliwość={frequency_id}, "
                    f"exclude_pinned={exclude_pinned}, przez={ctx.author}"
                )

                embed = create_embed(
                    title="✅ Harmonogram czyszczenia dodany",
                    description=f"Kanał {channel.mention} będzie czyszczony codziennie o **{clean_time}**",
                    color=discord.Color.green()
                )

                embed.add_field(name="ID kanału", value=str(channel.id), inline=True)
                embed.add_field(name="Wyklucz przypięte", value="✅ Tak" if exclude_pinned else "❌ Nie", inline=True)
                embed.add_field(name="Częstotliwość", value="Codziennie" if frequency_id == 1 else "Co tydzień",
                                inline=True)
                embed.set_footer(text=f"Dodane przez {ctx.author}")

                await ctx.send(embed=embed)
            else:
                self.logger.error(f"Błąd zapisu harmonogramu: {channel.id}")
                await ctx.send("❌ Nie udało się dodać harmonogramu")

        except Exception as e:
            self.logger.error(f"Błąd w komendzie !add: {e}", exc_info=True)
            await ctx.send("❌ Wystąpił nieoczekiwany błąd podczas dodawania harmonogramu")

    async def handle_add_debt_reminder(
        self,
        ctx,
        channel: discord.TextChannel,
        run_time: str,
        frequency_id: int = 1,
        message_template: str = ""
    ):
        await self.debt_reminder.handle(ctx, channel, run_time, frequency_id, message_template)

    # Nowe metody dla długów
    async def handle_add_debt(self, ctx, debtor: discord.Member, creditor: discord.Member,
                              amount: str, description: str = "", currency: str = "PLN"):
        """Obsługuje dodawanie długu"""
        try:
            amount_decimal = Decimal(amount)
            await self.debt_add.handle(ctx, debtor, creditor, amount_decimal, description, currency)
        except Exception as e:
            self.logger.error(f"Błąd w handle_add_debt: {e}", exc_info=True)
            await ctx.send("❌ Wystąpił błąd podczas dodawania długu")

    async def handle_settle_debt(self, ctx, debt_id: int):
        """Obsługuje spłatę długu"""
        await self.debt_settle.handle(ctx, debt_id)

    async def handle_list_debts(self, ctx, member: discord.Member = None, show_settled: bool = False):
        """Obsługuje listowanie długów"""
        await self.debt_list.handle(ctx, member, show_settled)

    # Aktualizacja istniejących metod
    async def handle_list(self, ctx):
        """Obsługuje komendę !list - pokazuje wszystkie harmonogramy"""
        cleaning_schedules = self.config_manager.get_all_cleaning_schedules()
        reminder_schedules = self.config_manager.get_debt_reminder_schedules(ctx.guild.id)

        if not cleaning_schedules and not reminder_schedules:
            embed = create_embed(
                title="📋 Harmonogramy",
                description="Brak aktywnych harmonogramów",
                color=discord.Color.blue()
            )
        else:
            embed = create_embed(
                title="📋 Harmonogramy",
                description=f"Czyszczenie: {len(cleaning_schedules)} | Przypomnienia: {len(reminder_schedules)}",
                color=discord.Color.blue()
            )

            # Harmonogramy czyszczenia
            if cleaning_schedules:
                cleaning_text = ""
                for schedule in cleaning_schedules[:5]:  # Ogranicz do 5
                    channel = self.bot.get_channel(schedule.channel_id)
                    channel_mention = channel.mention if channel else f"ID: {schedule.channel_id}"
                    cleaning_text += f"• {channel_mention} o **{schedule.time}**\n"

                if len(cleaning_schedules) > 5:
                    cleaning_text += f"\n...i {len(cleaning_schedules) - 5} więcej"

                embed.add_field(name="🧹 Czyszczenie", value=cleaning_text, inline=False)

            # Harmonogramy przypomnień
            if reminder_schedules:
                reminder_text = ""
                for schedule in reminder_schedules[:5]:  # Ogranicz do 5
                    channel = self.bot.get_channel(schedule.channel_id)
                    channel_mention = channel.mention if channel else f"ID: {schedule.channel_id}"
                    reminder_text += f"• {channel_mention} o **{schedule.run_time}**\n"

                if len(reminder_schedules) > 5:
                    reminder_text += f"\n...i {len(reminder_schedules) - 5} więcej"

                embed.add_field(name="💰 Przypomnienia o długach", value=reminder_text, inline=False)

        await ctx.send(embed=embed)

    async def handle_help(self, ctx):
        await self.help_command.handle(ctx)

    async def handle_avatar(self, ctx, member: discord.Member = None):
        await self.avatar_command.handle(ctx, member)

    async def handle_purge(self, ctx, amount: int, member: discord.Member = None):
        await self.purge_command.handle(ctx, amount, member)

    async def handle_whois(self, ctx, member: discord.Member = None):
        await self.whois_command.handle(ctx, member)

    async def handle_source_code(self, ctx):
        await self.source_code_command.handle(ctx)

    async def handle_uptime(self, ctx):
        await self.uptime_command.handle(ctx)

    async def handle_version(self, ctx):
        await self.version_command.handle(ctx)

    async def handle_ping(self, ctx):
        await self.ping_command.handle(ctx)

    async def handle_info(self, ctx):
        await self.info_command.handle(ctx)

    async def handle_coinflip(self, ctx):
        await self.coinflip_command.handle(ctx)

    async def handle_set_nickname(self, ctx, member: discord.Member, nickname: str):
        await self.set_nickname_command.handle(ctx, member, nickname)

    async def handle_delete_nickname(self, ctx, member: discord.Member):
        await self.delete_nickname.handle(ctx, member)

    async def handle_clean(self, ctx, amount: int):
        await self.clean_command.handle(ctx, amount)
