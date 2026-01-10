import discord

from utils.helpers import create_embed


class PingCommand:

    def __init__(self, bot, logger):
        self.bot = bot
        self.logger = logger

    async def handle(self, ctx):
        latency = round(self.bot.latency * 1000, 2)

        embed = create_embed(
            title="🏓 Ping",
            description=f"Opóźnienie bota: **{latency}ms**",
            color=discord.Color.green()
        )
        embed.set_footer(text=f"Żądane przez {ctx.author}", icon_url=ctx.author.display_avatar.url)

        await ctx.send(embed=embed)
