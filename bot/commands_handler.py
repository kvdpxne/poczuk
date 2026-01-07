"""
Komendy bota
"""
from datetime import datetime

import discord

from bot.commands import AvatarCommand, CoinflipCommand, UptimeCommand, SetNicknameCommand, HelpCommand
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
        """Obsługuje komendę !purge"""
        # Sprawdź uprawnienia
        if not ctx.channel.permissions_for(ctx.author).manage_messages:
            await ctx.send("❌ Brak uprawnień! Wymagane: Zarządzanie wiadomościami")
            return

        if not ctx.channel.permissions_for(ctx.guild.me).manage_messages:
            await ctx.send("❌ Bot nie ma uprawnień do zarządzania wiadomościami")
            return

        # Walidacja ilości
        if amount < 1:
            await ctx.send("❌ Podaj liczbę większą od 0")
            return
        if amount > 1000:
            await ctx.send("⚠️ Dla bezpieczeństwa maksymalna liczba to 1000")
            amount = 1000

        try:
            # Funkcja sprawdzająca dla filtru użytkownika
            check = None
            if member:
                # Tylko wiadomości tego użytkownika
                check = lambda m: m.author == member
            else:
                # Wszystkie wiadomości (bez filtru)
                check = lambda m: True  # Usuwa wszystkie wiadomości

            # Usuń wiadomości (limit + 1 aby uwzględnić komendę)
            deleted = await ctx.channel.purge(limit=amount + 1, check=check, oldest_first=False)

            # Odejmij komendę od liczby jeśli była usunięta
            deleted_count = len(deleted) - 1 if ctx.message in deleted else len(deleted)

            # Wyślij potwierdzenie
            embed = discord.Embed(
                title="🧹 Wiadomości wyczyszczone",
                description=f"Usunięto **{deleted_count}** wiadomości",
                color=discord.Color.green(),
                timestamp=datetime.now()
            )

            if member:
                embed.add_field(name="Filtr", value=f"Tylko wiadomości użytkownika {member.mention}", inline=False)
            else:
                embed.add_field(name="Filtr", value="Wszystkie wiadomości", inline=False)

            embed.add_field(name="Kanał", value=ctx.channel.mention, inline=True)
            embed.add_field(name="Przez", value=ctx.author.mention, inline=True)

            # Wiadomość usunie się po 5 sekundach
            msg = await ctx.send(embed=embed, delete_after=5.0)

            # Usuń również oryginalną komendę jeśli jeszcze istnieje
            try:
                await ctx.message.delete(delay=5.0)
            except:
                pass

        except discord.Forbidden:
            await ctx.send("❌ Brak uprawnień do usuwania wiadomości")
        except discord.HTTPException as e:
            await ctx.send(f"❌ Błąd podczas usuwania: {e}")

    async def handle_whois(self, ctx, member: discord.Member = None):
        """Obsługuje komendę !whois"""
        target = member or ctx.author

        # Tworzenie szczegółowego embed
        embed = discord.Embed(
            title=f"👤 Informacje o {target.display_name}",
            color=target.color if target.color != discord.Color.default() else discord.Color.purple(),
            timestamp=datetime.now()
        )

        # Ustaw avatar
        embed.set_thumbnail(url=target.display_avatar.url)

        # Podstawowe informacje
        embed.add_field(name="📝 Nazwa", value=f"{target.name}#{target.discriminator}", inline=True)
        embed.add_field(name="🆔 ID", value=target.id, inline=True)
        embed.add_field(name="🤖 Bot", value="Tak" if target.bot else "Nie", inline=True)

        # Daty
        embed.add_field(
            name="📅 Konto utworzone",
            value=f"<t:{int(target.created_at.timestamp())}:F>\n(<t:{int(target.created_at.timestamp())}:R>)",
            inline=False
        )

        if isinstance(target, discord.Member):
            embed.add_field(
                name="📅 Dołączył do serwera",
                value=f"<t:{int(target.joined_at.timestamp())}:F>\n(<t:{int(target.joined_at.timestamp())}:R>)",
                inline=False
            )

            # Role
            roles = [role.mention for role in target.roles[1:]]  # Pomijaj @everyone
            if roles:
                roles_text = " ".join(roles[-10:])  # Ostatnie 10 ról
                if len(roles) > 10:
                    roles_text += f"\n...i {len(roles) - 10} więcej"
                embed.add_field(name=f"🎭 Role ({len(roles)})", value=roles_text, inline=False)
            else:
                embed.add_field(name="🎭 Role", value="Brak ról", inline=False)

            # Najwyższa rola
            if target.top_role and target.top_role != ctx.guild.default_role:
                embed.add_field(name="👑 Najwyższa rola", value=target.top_role.mention, inline=True)

            # Administrator
            embed.add_field(name="⚙️ Administrator", value="Tak" if target.guild_permissions.administrator else "Nie",
                            inline=True)

            # Status
            status_emoji = {
                'online': '🟢',
                'idle': '🟡',
                'dnd': '🔴',
                'offline': '⚫'
            }
            embed.add_field(
                name="📱 Status",
                value=f"{status_emoji.get(str(target.status), '❓')} {str(target.status).upper()}",
                inline=True
            )

            # Aktywność
            if target.activity:
                activity_type = str(target.activity.type).split('.')[-1].title()
                embed.add_field(name="🎮 Aktywność", value=f"{activity_type}: {target.activity.name}", inline=False)

        # Booster
        if hasattr(target, 'premium_since') and target.premium_since:
            embed.add_field(
                name="🌟 Booster",
                value=f"Od <t:{int(target.premium_since.timestamp())}:R>",
                inline=True
            )

        embed.set_footer(text=f"Żądane przez {ctx.author}", icon_url=ctx.author.display_avatar.url)

        await ctx.send(embed=embed)

    async def handle_sourcecode(self, ctx):
        """Obsługuje komendę !sourcecode"""
        self.logger.info(f"Komenda !sourcecode wywołana przez {ctx.author} ({ctx.author.id})")

        embed = discord.Embed(
            title="📦 Kod źródłowy",
            color=discord.Color.dark_grey(),
            timestamp=get_current_datetime()
        )

        embed.add_field(
            name="Repozytorium",
            value="https://github.com/kvdpxne/poczuk",
            inline=False
        )

        embed.add_field(
            name="Licencja",
            value="WTFPL (Do What The Fuck You Want To Public License)",
            inline=True
        )

        embed.add_field(
            name="Status",
            value="Open Source",
            inline=True
        )

        embed.add_field(
            name="Technologie",
            value="Python 3.12+, discord.py 2.0+",
            inline=False
        )

        embed.set_footer(text=f"Żądane przez {ctx.author}", icon_url=ctx.author.display_avatar.url)

        await ctx.send(embed=embed)

    async def handle_uptime(self, ctx):
        await self.uptime_command.handle(ctx)

    async def handle_ping(self, ctx):
        await self.ping_command.handle(ctx)

    async def handle_info(self, ctx):
        """Obsługuje komendę !info - wyświetla informacje o bocie"""
        import psutil
        import os
        from utils.helpers import get_current_datetime

        # Pobierz dane
        schedules = self.config_manager.load_schedules()
        schedule_count = len(schedules)

        # Statystyki systemowe
        process = psutil.Process(os.getpid())
        memory_mb = process.memory_info().rss / 1024 / 1024
        cpu_percent = process.cpu_percent(interval=0.1)

        # Statystyki bota
        guild_count = len(self.bot.guilds)
        total_members = sum(guild.member_count for guild in self.bot.guilds)

        embed = create_embed(
            title="🤖 Informacje o bocie",
            description="Discord Channel Cleaner - automatyczne czyszczenie kanałów",
            color=discord.Color.blue()
        )

        embed.add_field(name="Wersja", value="2.0", inline=True)
        embed.add_field(name="Autor", value="kvdpxne", inline=True)
        embed.add_field(name="Prefix", value="!", inline=True)

        embed.add_field(name="Serwery", value=str(guild_count), inline=True)
        embed.add_field(name="Użytkownicy", value=str(total_members), inline=True)
        embed.add_field(name="Harmonogramy", value=str(schedule_count), inline=True)

        embed.add_field(name="💾 RAM", value=f"{memory_mb:.1f} MB", inline=True)
        embed.add_field(name="⚡ CPU", value=f"{cpu_percent:.1f}%", inline=True)
        embed.add_field(name="🏓 Ping", value=f"{round(self.bot.latency * 1000)}ms", inline=True)

        embed.add_field(
            name="📦 Kod źródłowy",
            value="[GitHub](https://github.com/kvdpxne/poczuk)",
            inline=False
        )

        embed.add_field(
            name="📋 Licencja",
            value="WTFPL (Do What The Fuck You Want To Public License)",
            inline=True
        )

        embed.set_footer(text=f"Żądane przez {ctx.author}", icon_url=ctx.author.display_avatar.url)

        await ctx.send(embed=embed)

    async def handle_coinflip(self, ctx):
        await self.coinflip_command.handle(ctx)

    async def handle_set_nickname(self, ctx, member: discord.Member, nickname: str):
        await self.set_nickname_command.handle(ctx, member, nickname)

    async def handle_delete_nickname(self, ctx, member: discord.Member):
        await self.delete_nickname.handle(ctx, member)
