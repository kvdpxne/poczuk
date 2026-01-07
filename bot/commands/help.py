"""
Moduł komendy !flipcoin
"""
import discord

from utils.helpers import create_embed


class HelpCommand:
    """Obsługa komendy !flipcoin"""

    def __init__(self, bot, logger):
        self.bot = bot
        self.logger = logger

    async def handle(self, ctx):
        """Obsługuje komendę !help"""
        embed = create_embed(
            title="🤖 Discord Cleaner - Pomoc",
            description="Bot do automatycznego czyszczenia kanałów",
            color=discord.Color.purple()
        )

        commands_info = [
            ("!add #kanał HH:MM", "Dodaje codzienne czyszczenie kanału"),
            ("!remove #kanał", "Usuwa harmonogram czyszczenia"),
            ("!list", "Wyświetla wszystkie harmonogramy"),
            ("!test [#kanał]", "Testowe czyszczenie kanału"),
            ("!purge <liczba> [@użytkownik]", "Czyści określoną liczbę wiadomości"),
            ("!avatar [@użytkownik]", "Pokazuje avatar użytkownika"),
            ("!whois [@użytkownik]", "Pokazuje informacje o użytkowniku"),
            ("!uptime", "Pokazuje czas działania bota"),
            ("!ping", "Pokazuje opóźnienie bota (ping)"),
            ("!info", "Pokazuje informacje o bocie"),
            ("!flipcoin", "Rzut monetą (alias: !coinflip) - 48% orzeł, 48% reszka, 1% krawędź, 1% zgubienie"),
            ("!sourcecode", "Informacje o kodzie źródłowym (aliasy: !source, !src)"),
            ("!help", "Wyświetla tę wiadomość")
        ]

        for cmd, desc in commands_info:
            embed.add_field(name=cmd, value=desc, inline=False)

        embed.set_footer(text="Wymagane uprawnienia: Administrator")

        await ctx.send(embed=embed)
