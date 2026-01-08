"""
Moduł komendy !info - pokazuje informacje o bocie
"""
import discord
import psutil
import os
from utils.helpers import create_embed, get_current_datetime


class InfoCommand:
    """Obsługa komendy !info"""

    def __init__(self, bot, config_manager, logger):
        self.bot = bot
        self.config_manager = config_manager
        self.logger = logger

    async def handle(self, ctx):
        """Główna metoda obsługi komendy"""
        try:
            self.logger.info(f"Komenda !info wywołana przez {ctx.author} ({ctx.author.id})")

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
                color=discord.Color.blue(),
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

        except Exception as e:
            self.logger.error(f"Błąd w komendzie !info: {e}", exc_info=True)
            await ctx.send("❌ Wystąpił błąd podczas pobierania informacji o bocie")