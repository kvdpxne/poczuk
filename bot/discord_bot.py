"""
Główna klasa bota Discord - Open/Closed Principle
"""
import discord
from discord.ext import commands
from config.config_manager import ConfigManager
from config.token_manager import TokenManager
from scheduler.scheduler import Scheduler
from utils.logger import get_module_logger, log_bot_ready
from bot.commands_handler import CommandHandler


class DiscordBot(commands.Bot):
    """Główna klasa bota Discord Cleaner"""

    def __init__(self):
        # Inicjalizacja loggera
        self.logger = get_module_logger(__name__)

        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        activity = discord.Activity(
            type=discord.ActivityType.listening,
            name="get some help | $help"
        )

        super().__init__(
            command_prefix='$',
            intents=intents,
            help_command=None,
            activity=activity
        )

        # Inicjalizacja menedżerów
        self.config_manager = ConfigManager()
        self.token_manager = TokenManager()

        # Inicjalizacja komponentów
        self.scheduler = Scheduler(self, self.config_manager)
        self.command_handler = CommandHandler(self, self.config_manager, self.scheduler)

        # Ustawienie eventów
        self._setup_events()

        self.logger.info("Zainicjalizowano bota DiscordBot")

    def _setup_events(self):
        """Konfiguruje eventy bota"""

        @self.event
        async def on_ready():
            await self._on_ready_handler()

        @self.event
        async def on_command_error(ctx, error):
            await self._on_command_error_handler(ctx, error)

        @self.event
        async def on_message(message):
            """Przetwarza wszystkie wiadomości i wywołuje komendy"""
            # Ignoruj wiadomości od botów (w tym własne)
            if message.author.bot:
                return

            # Przetwarzaj komendy
            ctx = await self.get_context(message)

            if ctx.command:
                # Logowanie komendy przed wykonaniem
                from utils.logger import log_command
                log_command(ctx)

            await self.invoke(ctx)

        @self.command(name="add")
        @commands.has_permissions(administrator=True)
        async def add_command(ctx, channel: discord.TextChannel, clean_time: str):
            await self.command_handler.handle_add(ctx, channel, clean_time)

        @self.command(name="remove")
        @commands.has_permissions(administrator=True)
        async def remove_command(ctx, channel: discord.TextChannel):
            await self.command_handler.handle_remove(ctx, channel)

        @self.command(name="list")
        async def list_command(ctx):
            await self.command_handler.handle_list(ctx)

        @self.command(name="test")
        @commands.has_permissions(administrator=True)
        async def test_command(ctx, channel: discord.TextChannel = None):
            await self.command_handler.handle_test(ctx, channel)

        @self.command(name="help")
        async def help_command(ctx):
            await self.command_handler.handle_help(ctx)

        @self.command(name="avatar")
        async def avatar_command(ctx, member: discord.Member = None):
            await self.command_handler.handle_avatar(ctx, member)

        @self.command(name="purge")
        @commands.has_permissions(manage_messages=True)
        async def purge_command(ctx, amount: int, member: discord.Member = None):
            await self.command_handler.handle_purge(ctx, amount, member)

        @self.command(name="whois")
        async def whois_command(ctx, member: discord.Member = None):
            await self.command_handler.handle_whois(ctx, member)

        @self.command(name="sourcecode", aliases=["source", "src"])
        async def sourcecode_command(ctx):
            await self.command_handler.handle_sourcecode(ctx)

        @self.command(name="uptime")
        async def uptime_command(ctx):
            await self.command_handler.handle_uptime(ctx)

        @self.command(name="ping")
        async def ping_command(ctx):
            await self.command_handler.handle_ping(ctx)

        @self.command(name="info")
        async def info_command(ctx):
            await self.command_handler.handle_info(ctx)

        @self.command(name="flipcoin", aliases=["coinflip"])
        async def flipcoin_command(ctx):
            await self.command_handler.handle_coinflip(ctx)

        @self.command(name="SetNickname", aliases=["SetNick", 'SetName', 'AddNickname', 'AddNick', 'AddName'])
        @commands.has_permissions(manage_nicknames=True)
        async def set_nickname_command(ctx, member: discord.Member, nickname: str):
            await self.command_handler.handle_set_nickname(ctx, member, nickname)

        @self.command(name="clearnick", aliases=["removenick", "deletenick"])
        @commands.has_permissions(manage_nicknames=True)
        async def clearnick_command(ctx, member: discord.Member):
            await self.command_handler.handle_delete_nickname(ctx, member)

    async def _on_ready_handler(self):
        """Obsługa eventu on_ready"""
        from datetime import datetime

        # Zaloguj informacje o starcie
        schedule_count = len(self.config_manager.load_schedules())
        log_bot_ready(self.user, len(self.guilds), schedule_count)

        # Ustaw czas startu dla komendy status
        self.start_time = datetime.now()

        # Uruchom harmonogram
        self.loop.create_task(self.scheduler.start())
        self.logger.info("Uruchomiono harmonogram czyszczenia")

    async def _on_command_error_handler(self, ctx, error):
        """Obsługa błędów komend"""
        from utils.logger import log_error

        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Brak uprawnień! Wymagana rola: Administrator")
            self.logger.warning(f"Brak uprawnień: {ctx.author} próbował użyć {ctx.command.name}")
        elif isinstance(error, commands.ChannelNotFound):
            await ctx.send("❌ Nie znaleziono kanału. Upewnij się, że podałeś poprawną nazwę/ID.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Brakujący argument. Użyj: `{ctx.command.signature}`")
        else:
            await ctx.send(f"❌ Błąd: {str(error)}")
            log_error('commands', error, f"Komenda: {ctx.command.name}, Użytkownik: {ctx.author}")

    def run_bot(self):
        """Uruchamia bota"""
        token = self.token_manager.load_token()

        if not token:
            self.logger.warning("Brak tokenu w pliku, wymagane ręczne podanie")
            print("\n" + "="*50)
            print("PIERWSZE URUCHOMIENIE")
            print("="*50)

            token = input("\nPodaj token bota Discord: ").strip()

            if self.token_manager.save_token(token):
                self.logger.info("Token zapisany do pliku")
            else:
                self.logger.error("Nie udało się zapisać tokenu")
                return

        self.logger.info("Uruchamiam bota...")
        self.run(token)