import discord

from utils.helpers import create_embed


class HelpCommand:

    def __init__(self, bot, logger):
        self.bot = bot
        self.logger = logger

    async def handle(self, ctx):
        embed = create_embed(
            title="📖 Pomoc - Discord Cleaner",
            description="Wszystkie komendy i szczegółowa dokumentacja dostępne są w wiki projektu.",
            color=discord.Color.blue()
        )

        embed.add_field(
            name="🌐 Pełna dokumentacja",
            value="[**Przejdź do wiki z komendami**](https://github.com/kvdpxne/poczuk/wiki/Commands)",
            inline=False
        )

        embed.add_field(
            name="💡 Szybka informacja",
            value="• Prefix: `$` (niewrażliwy na wielkość liter)\n• Problemy? Sprawdź wiki!",
            inline=False
        )

        embed.set_footer(
            text=f"Żądane przez {ctx.author}",
            icon_url=ctx.author.display_avatar.url
        )

        await ctx.send(embed=embed)
