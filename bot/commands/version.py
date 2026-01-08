"""
Moduł komendy !version
"""
import discord
from datetime import datetime
from utils.git_version import get_git_version


class VersionCommand:
    """Obsługa komendy !version"""

    def __init__(self, bot, logger):
        self.bot = bot
        self.logger = logger
        self.git_version = get_git_version()

    async def handle(self, ctx):
        """Główna metoda obsługi komendy"""
        try:
            self.logger.info(f"Komenda !version wywołana przez {ctx.author} ({ctx.author.id})")

            # Pobierz dane do embeda
            embed_data = self.git_version.get_version_embed_data()

            # Tworzenie embed
            embed = discord.Embed(
                title=embed_data["title"],
                description=embed_data["description"],
                color=embed_data["color"],
                timestamp=datetime.now()
            )

            # Dodaj pola
            for field in embed_data.get("fields", []):
                embed.add_field(
                    name=field["name"],
                    value=field["value"],
                    inline=field.get("inline", True)
                )

            # Dodaj footer jeśli istnieje
            if embed_data.get("footer"):
                footer_text = embed_data["footer"].get("text", "")
                embed.set_footer(text=footer_text)
            else:
                embed.set_footer(
                    text=f"Żądane przez {ctx.author}",
                    icon_url=ctx.author.display_avatar.url
                )

            await ctx.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Błąd w komendzie !version: {e}", exc_info=True)
            await ctx.send("❌ Wystąpił błąd podczas pobierania informacji o wersji")


# Funkcja pomocnicza do szybkiego dostępu
async def send_version_info(ctx, bot, logger):
    """Szybka funkcja do wysłania informacji o wersji"""
    cmd = VersionCommand(bot, logger)
    await cmd.handle(ctx)