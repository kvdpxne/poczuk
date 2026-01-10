import discord

from utils.helpers import create_embed


class UptimeCommand:

    def __init__(self, bot, logger):
        self.bot = bot
        self.logger = logger

    async def handle(self, ctx):
        from datetime import datetime

        now = datetime.now()
        uptime = now - self.bot.start_time

        # Formatowanie czasu
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        uptime_str = f"{days}d {hours}h {minutes}m {seconds}s"

        embed = create_embed(
            title="⏱️ Uptime",
            description=f"Bot działa od: <t:{int(self.bot.start_time.timestamp())}:R>",
            color=discord.Color.green()
        )
        embed.add_field(name="Czas działania", value=uptime_str, inline=True)
        embed.set_footer(text=f"Żądane przez {ctx.author}", icon_url=ctx.author.display_avatar.url)

        await ctx.send(embed=embed)
