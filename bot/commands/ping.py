import discord
import time
from utils.helpers import create_embed


class PingCommand:

    def __init__(self, bot, logger):
        self.bot = bot
        self.logger = logger

    async def handle(self, ctx):
        # Wysłanie początkowej wiadomości i zmierzenie czasu
        start_time = time.perf_counter()

        # Wyślij początkową wiadomość tekstową
        message = await ctx.send("🏓 Ping...")

        # Zmierzenie czasu odpowiedzi
        end_time = time.perf_counter()
        rtt_latency = round((end_time - start_time) * 1000, 2)

        # Opóźnienie WebSocket
        ws_latency = round(self.bot.latency * 1000, 2)

        # Utworzenie embed z pomiarami
        embed = create_embed(
            title="🏓 Pong!",
            description=(
                f"**Opóźnienie WebSocket:** {ws_latency}ms\n"
                f"**Opóźnienie odpowiedzi (RTT):** {rtt_latency}ms"
            ),
            color=discord.Color.green(),
            author=ctx.author,
            icon_url=ctx.author.display_avatar.url,
        )

        # Edycja wiadomości na embed z wynikami
        await message.edit(content=None, embed=embed)