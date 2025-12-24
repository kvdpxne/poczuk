"""
Główna klasa bota Discord
"""
import discord
from discord.ext import commands
from config.config_manager import ConfigManager
from config.token_manager import TokenManager
from scheduler.scheduler import Scheduler
from bot.commands import CommandHandler


class DiscordBot(commands.Bot):
    """Główna klasa bota Discord Cleaner"""

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        activity = discord.Activity(
            type=discord.ActivityType.listening,
            name="get some help | $help"
        )

        super().__init__(
            command_prefix='$',
            help_command=None,
            intents=intents,
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

    def _setup_events(self):
        """Konfiguruje eventy bota"""

        @self.event
        async def on_ready():
            await self._on_ready_handler()

        @self.event
        async def on_command_error(ctx, error):
            await self._on_command_error_handler(ctx, error)

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

        @self.command(name="status")
        @commands.has_permissions(administrator=True)
        async def status_command(ctx):
            await self.command_handler.handle_status(ctx)

    async def _on_ready_handler(self):
        """Obsługa eventu on_ready"""
        from datetime import datetime

        print(f"\n{'=' * 50}")
        print(f"Bot zalogowany jako: {self.user.name}")
        print(f"ID: {self.user.id}")
        print(f"Liczba harmonogramów: {len(self.config_manager.load_schedules())}")
        print(f"Gildie: {len(self.guilds)}")
        print(f"{'=' * 50}\n")

        # Ustaw czas startu dla komendy status
        self.start_time = datetime.now()

        # Uruchom harmonogram
        self.loop.create_task(self.scheduler.start())

    async def _on_command_error_handler(self, ctx, error):
        """Obsługa błędów komend"""
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Brak uprawnień! Wymagana rola: Administrator")
        elif isinstance(error, commands.ChannelNotFound):
            await ctx.send("❌ Nie znaleziono kanału. Upewnij się, że podałeś poprawną nazwę/ID.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Brakujący argument. Użyj: `{ctx.command.signature}`")
        else:
            await ctx.send(f"❌ Błąd: {str(error)}")

    def run_bot(self):
        """Uruchamia bota"""
        token = self.token_manager.load_token()

        if not token:
            print("\n" + "=" * 50)
            print("PIERWSZE URUCHOMIENIE")
            print("=" * 50)

            token = input("\nPodaj token bota Discord: ").strip()

            if self.token_manager.save_token(token):
                print("\nToken zapisany w data/token.txt")
            else:
                print("\n❌ Nie udało się zapisać tokenu")
                return

        print("\nUruchamiam bota...\n")
        self.run(token)
