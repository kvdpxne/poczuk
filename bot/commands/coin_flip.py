import random
from datetime import datetime

import discord


class CoinFlipCommand:

    def __init__(self, bot, logger):
        self.bot = bot
        self.logger = logger

    async def handle(self, ctx):
        """Główna metoda obsługi komendy"""
        try:
            self.logger.info(f"Komenda !flipcoin wywołana przez {ctx.author} ({ctx.author.id})")

            # Losowanie z podanymi prawdopodobieństwami
            rand = random.random()  # Zwraca liczbę z przedziału [0.0, 1.0)

            if rand < 0.48:
                result = "orzeł"
                emoji = "🦅"
                description = "Moneta pokazała orła! (48% szansy)"
                color = discord.Color.gold()
            elif rand < 0.96:  # 0.48 + 0.48 = 0.96
                result = "reszka"
                emoji = "🪙"
                description = "Moneta pokazała reszkę! (48% szansy)"
                color = discord.Color.dark_grey()
            elif rand < 0.97:  # 0.96 + 0.01 = 0.97
                result = "krawędź"
                emoji = "⚖️"
                description = "Niewiarygodne! Moneta stanęła na krawędzi! (1% szansy)"
                color = discord.Color.orange()
            else:  # 0.97 + 0.01 = 0.98 (w zaokrągleniu, ale random() < 1.0)
                result = "zgubiona"
                emoji = "❓"
                description = "Moneta gdzieś się zgubiła... (1% szansy) Spróbuj ponownie!"
                color = discord.Color.dark_red()

            # Tworzenie embed
            embed = discord.Embed(
                title=f"{emoji} Rzut monetą",
                description=description,
                color=color,
                timestamp=datetime.now()
            )

            embed.add_field(name="Wynik", value=result.capitalize(), inline=True)
            embed.add_field(name="Wartość losowania", value=f"{rand:.4f}", inline=True)

            # Statystyki prawdopodobieństwa
            stats = "• Orzeł: 48%\n• Reszka: 48%\n• Krawędź: 1%\n• Zgubiona: 1%"
            embed.add_field(name="Szczegółowe prawdopodobieństwa", value=stats, inline=False)

            embed.set_footer(text=f"Żądane przez {ctx.author}", icon_url=ctx.author.display_avatar.url)

            await ctx.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Błąd w komendzie !flipcoin: {e}", exc_info=True)
            await ctx.send("❌ Wystąpił błąd podczas rzutu monetą")
