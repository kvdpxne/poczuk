import discord
from discord.ext import commands

from bot.commands_handler import CommandHandler
from config.config_manager import ConfigManager
from config.token_manager import TokenManager
from scheduler.scheduler import Scheduler
from utils.logger import get_logger, log_info, log_command


class DiscordBot(commands.Bot):
    """Główna klasa bota Discord Cleaner"""

    def __init__(self):
        # UŻYJ get_logger ZAMIast get_module_logger
        self.logger = get_logger(__name__)

        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        activity = discord.Activity(
            type=discord.ActivityType.listening,
            name="get some help | $help"
        )

        super().__init__(
            command_prefix='$',
            case_insensitive=True,
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

        @self.event
        async def on_ready():
            await self._on_ready_handler()

        @self.event
        async def on_message(message):
            """Przetwarza wszystkie wiadomości i wywołuje komendy"""
            # Ignoruj wiadomości od botów (w tym własne)
            if message.author.bot:
                return

            await self.process_commands(message)

        @self.event
        async def on_command(ctx):
            """Logowanie każdej wykonanej komendy"""
            log_command(ctx)

        @self.event
        async def on_command_error(ctx, error):
            await self._on_command_error_handler(ctx, error)


        @self.command(name="adddebt", aliases=["debtadd", "dodajdlug"])
        @commands.has_permissions(administrator=True)
        async def add_debt_command(ctx, debtor: discord.Member, creditor: discord.Member,
                                   amount: str, *, description: str = ""):
            await self.command_handler.handle_add_debt(ctx, debtor, creditor, amount, description)

        @self.command(name="settledebt", aliases=["debtpay", "splacdlug"])
        @commands.has_permissions(administrator=True)
        async def settle_debt_command(ctx, debt_id: int):
            await self.command_handler.handle_settle_debt(ctx, debt_id)

        @self.command(name="listdebts", aliases=["debts", "dlugi"])
        async def list_debts_command(ctx, member: discord.Member = None):
            await self.command_handler.handle_list_debts(ctx, member)

        @self.command(name="addreminder", aliases=["remindadd", "dodajprzypomnienie"])
        @commands.has_permissions(administrator=True)
        async def add_reminder_command(ctx, channel: discord.TextChannel, run_time: str,
                                       frequency: str = "daily", *, message_template: str = ""):
            frequency_map = {"daily": 1, "weekly": 2}
            frequency_id = frequency_map.get(frequency.lower(), 1)
            await self.command_handler.handle_add_debt_reminder(ctx, channel, run_time, frequency_id, message_template)




        # Zmień deklarację komendy add na:
        @self.command(name="add")
        @commands.has_permissions(administrator=True)
        async def add_command(ctx, channel: discord.TextChannel, clean_time: str, options: str = ""):
            await self.command_handler.handle_add(ctx, channel, clean_time, options)

        @self.command(name="remove")
        @commands.has_permissions(administrator=True)
        async def remove_command(ctx, channel: discord.TextChannel):
            await self.command_handler.handle_remove(ctx, channel)

        @self.command(name="list")
        async def list_command(ctx):
            await self.command_handler.handle_list(ctx)

        @self.command(name="help", aliases=['h'])
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

        @self.command(name="SourceCode", aliases=["source", "src", "github"])
        async def sourcecode_command(ctx):
            await self.command_handler.handle_source_code(ctx)

        @self.command(name="uptime")
        async def uptime_command(ctx):
            await self.command_handler.handle_uptime(ctx)

        @self.command(name="ping")
        async def ping_command(ctx):
            await self.command_handler.handle_ping(ctx)

        @self.command(name="info")
        async def info_command(ctx):
            await self.command_handler.handle_info(ctx)

        @self.command(name="CoinFlip", aliases=["FlipCoin"])
        async def coinflip_command(ctx):
            await self.command_handler.handle_coinflip(ctx)

        @self.command(name="SetNickname", aliases=["SetNick", 'SetName', 'AddNickname', 'AddNick', 'AddName'])
        @commands.has_permissions(manage_nicknames=True)
        async def set_nickname_command(ctx, member: discord.Member, nickname: str):
            await self.command_handler.handle_set_nickname(ctx, member, nickname)

        @self.command(name="DeleteNickname",
                      aliases=["DeleteNick", "DeleteName", "RemoveNickname", "RemoveNick", "RemoveName"])
        @commands.has_permissions(manage_nicknames=True)
        async def delete_nickname_command(ctx, member: discord.Member):
            await self.command_handler.handle_delete_nickname(ctx, member)

        @self.command(name="version", aliases=["ver", "v"])
        async def version_command(ctx):
            await self.command_handler.handle_version(ctx)

        @self.command(name="Clean", aliases=["CleanBot", "Clear", "ClearBot"])
        @commands.has_permissions(manage_messages=True)
        async def clean_command(ctx, amount: int):
            await self.command_handler.handle_clean(ctx, amount)

    async def _on_ready_handler(self):
        """Obsługa eventu on_ready"""
        from datetime import datetime

        # Zaloguj informacje o starcie
        schedule_count = len(self.config_manager.load_schedules())

        log_info('main', f"Bot zalogowany jako: {self.user.name} ({self.user.id})")
        log_info('main', f"Liczba serwerów: {len(self.guilds)}")
        log_info('main', f"Liczba harmonogramów: {schedule_count}")
        log_info('main', "=" * 50)

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
            log_error('commands', error, f"Komenda: Nieznana, Użytkownik: {ctx.author}")
            # log_error('commands', error, f"Komenda: {ctx.command.name}, Użytkownik: {ctx.author}")

    def run_bot(self):
        token = self.token_manager.load_token()

        if not token:
            self.logger.error("Token nie znaleziony w zmiennych środowiskowych!")
            print("\n" + "=" * 60)
            print("❌ BRAK TOKENU DISCORD")
            print("=" * 60)
            print("\nSposoby konfiguracji tokenu:\n")

            print("Metoda 1: Plik .env (najlepsza):")
            print("   echo 'DISCORD_BOT_TOKEN=twój_token' > .env")
            print("   # DODAJ .env DO .gitignore!")

            return

        self.logger.info("Uruchamiam bota...")
        self.run(token)
