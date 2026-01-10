import discord

from utils.helpers import create_embed


class SourceCodeCommand:

    def __init__(self, bot, logger):
        self.bot = bot
        self.logger = logger

    async def handle(self, ctx):
        try:
            self.logger.info(f"Komenda !sourcecode wywołana przez {ctx.author} ({ctx.author.id})")

            embed = create_embed(
                title="📦 Kod źródłowy",
                color=discord.Color.dark_grey(),
                description=""
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

        except Exception as e:
            self.logger.error(f"Błąd w komendzie !sourcecode: {e}", exc_info=True)
            await ctx.send("❌ Wystąpił błąd podczas pobierania informacji o kodzie źródłowym")
