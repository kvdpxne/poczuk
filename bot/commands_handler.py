"""
Komendy bota
"""

import discord

from bot.commands import AvatarCommand, CoinflipCommand, UptimeCommand, SetNicknameCommand, HelpCommand, VersionCommand, \
    WhoisCommand, InfoCommand, PurgeCommand, SourceCodeCommand, CleanCommand
from bot.commands.delete_nickname import DeleteNicknameCommand
from bot.commands.ping import PingCommand
from models.channel_schedule import ChannelSchedule
from utils import get_module_logger
from utils.helpers import create_embed, format_channel_mention, get_current_datetime
from utils.validators import TimeValidator


class CommandHandler:
    """Obsługa komend bota"""

    def __init__(self, bot, config_manager, scheduler):
        self.logger = get_module_logger(__name__)
        self.bot = bot
        self.config_manager = config_manager
        self.scheduler = scheduler
        self.validator = TimeValidator()

        # Inicjalizacja modułów komend
        self.avatar_command = AvatarCommand(bot, self.logger)
        self.coinflip_command = CoinflipCommand(bot, self.logger)
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

    async def handle_add(self, ctx, channel: discord.TextChannel, clean_time: str):
        """Obsługuje komendę !add"""
        # Walidacja czasu
        if not self.validator.validate_time_format(clean_time):
            return await ctx.send("❌ Nieprawidłowy format czasu. Użyj HH:MM (np. 03:00)")

        # Sprawdź czy kanał już ma harmonogram
        existing = self.config_manager.get_schedule(channel.id)
        if existing:
            return await ctx.send(
                f"❌ Kanał {channel.mention} już ma ustawione czyszczenie o {existing.time}"
            )

        # Utwórz nowy harmonogram
        new_schedule = ChannelSchedule(
            channel_id=channel.id,
            channel_name=channel.name,
            time=clean_time,
            added_by=ctx.author.id,
            added_at=get_current_datetime()
        )

        # Zapisz harmonogram
        if self.config_manager.add_schedule(new_schedule):
            embed = create_embed(
                title="✅ Harmonogram dodany",
                description=f"Kanał {channel.mention} będzie czyszczony codziennie o **{clean_time}**",
                color=discord.Color.green()
            )
            embed.add_field(name="ID kanału", value=str(channel.id))
            embed.add_field(
                name="Liczba harmonogramów",
                value=str(len(self.config_manager.load_schedules()))
            )
            embed.set_footer(text=f"Dodane przez {ctx.author}")

            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ Nie udało się dodać harmonogramu")

    async def handle_remove(self, ctx, channel: discord.TextChannel):
        """Obsługuje komendę !remove"""
        if self.config_manager.remove_schedule(channel.id):
            embed = create_embed(
                title="🗑️ Harmonogram usunięty",
                description=f"Usunięto harmonogram czyszczenia dla {channel.mention}",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"❌ Nie znaleziono harmonogramu dla {channel.mention}")

    async def handle_list(self, ctx):
        """Obsługuje komendę !list"""
        schedules = self.config_manager.load_schedules()

        if not schedules:
            embed = create_embed(
                title="📋 Harmonogramy czyszczenia",
                description="Brak aktywnych harmonogramów",
                color=discord.Color.blue()
            )
        else:
            embed = create_embed(
                title="📋 Harmonogramy czyszczenia",
                description=f"Liczba aktywnych harmonogramów: {len(schedules)}",
                color=discord.Color.blue()
            )

            for schedule in schedules:
                channel_mention = format_channel_mention(self.bot, schedule.channel_id)

                embed.add_field(
                    name=f"⏰ {schedule.time}",
                    value=f"Kanał: {channel_mention}\nID: {schedule.channel_id}",
                    inline=False
                )

        await ctx.send(embed=embed)

    async def handle_test(self, ctx, channel: discord.TextChannel = None):
        """Obsługuje komendę !test"""
        target_channel = channel or ctx.channel

        embed = create_embed(
            title="🧪 Test czyszczenia",
            description=f"Rozpoczynam testowe czyszczenie {target_channel.mention}...",
            color=discord.Color.yellow()
        )

        msg = await ctx.send(embed=embed)
        deleted_count = await self.scheduler.execute_test_clean(target_channel.id)

        embed = create_embed(
            title="✅ Test zakończony",
            description=f"Usunięto {deleted_count} wiadomości z {target_channel.mention}",
            color=discord.Color.green()
        )

        try:
            await msg.edit(embed=embed)
        except discord.NotFound:
            # Jeśli wiadomość została usunięta podczas czyszczenia, wyślij nową
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
