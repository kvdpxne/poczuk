"""
Moduł komendy !purge - czyści określoną liczbę wiadomości
"""
import discord
import asyncio
from utils.helpers import create_embed, get_current_datetime


class PurgeCommand:
    """Obsługa komendy !purge"""

    def __init__(self, bot, logger):
        self.bot = bot
        self.logger = logger

    async def handle(self, ctx, amount: int, member: discord.Member = None):
        """Główna metoda obsługi komendy"""
        try:
            # Sprawdź uprawnienia
            if not ctx.channel.permissions_for(ctx.author).manage_messages:
                self.logger.warning(f"Brak uprawnień do purge: {ctx.author}")
                await ctx.send("❌ Brak uprawnień! Wymagane: Zarządzanie wiadomościami")
                return

            if not ctx.channel.permissions_for(ctx.guild.me).manage_messages:
                self.logger.warning(f"Bot bez uprawnień do purge na kanale: {ctx.channel.id}")
                await ctx.send("❌ Bot nie ma uprawnień do zarządzania wiadomościami")
                return

            # Walidacja ilości
            if amount < 1:
                await ctx.send("❌ Podaj liczbę większą od 0")
                return
            if amount > 1000:
                self.logger.warning(f"Próba usunięcia {amount} wiadomości, ograniczono do 1000")
                await ctx.send("⚠️ Dla bezpieczeństwa maksymalna liczba to 1000")
                amount = 1000

            # Log rozpoczęcia czyszczenia
            self.logger.info(
                f"Rozpoczynanie purge: ilość={amount}, "
                f"kanał={ctx.channel.name} ({ctx.channel.id}), "
                f"użytkownik={ctx.author}, "
                f"filtr={'wszyscy' if not member else member}"
            )

            # Funkcja sprawdzająca dla filtru użytkownika
            check = None
            if member:
                check = lambda m: m.author == member
            else:
                check = lambda m: True

            # Usuń wiadomości
            deleted = await ctx.channel.purge(limit=amount + 1, check=check, oldest_first=False)

            # Odejmij komendę od liczby
            deleted_count = len(deleted) - 1 if ctx.message in deleted else len(deleted)

            # Log zakończenia
            self.logger.info(
                f"Zakończono purge: usunięto={deleted_count} wiadomości, "
                f"kanał={ctx.channel.name} ({ctx.channel.id})"
            )

            # Wyślij potwierdzenie
            embed = create_embed(
                title="🧹 Wiadomości wyczyszczone",
                description=f"Usunięto **{deleted_count}** wiadomości",
                color=discord.Color.green(),
                timestamp=get_current_datetime()
            )

            if member:
                embed.add_field(name="Filtr", value=f"Tylko wiadomości użytkownika {member.mention}", inline=False)
            else:
                embed.add_field(name="Filtr", value="Wszystkie wiadomości", inline=False)

            embed.add_field(name="Kanał", value=ctx.channel.mention, inline=True)
            embed.add_field(name="Przez", value=ctx.author.mention, inline=True)

            # Wiadomość usunie się po 5 sekundach
            msg = await ctx.send(embed=embed, delete_after=5.0)

            # Usuń również oryginalną komendę jeśli jeszcze istnieje
            try:
                await ctx.message.delete(delay=5.0)
            except:
                pass

        except discord.Forbidden:
            self.logger.error(f"Brak uprawnień do usuwania wiadomości na kanale {ctx.channel.id}")
            await ctx.send("❌ Brak uprawnień do usuwania wiadomości")
        except discord.HTTPException as e:
            self.logger.error(f"Błąd HTTP podczas purge: {e}")
            await ctx.send(f"❌ Błąd podczas usuwania: {e}")
        except Exception as e:
            self.logger.error(f"Nieoczekiwany błąd w purge: {e}", exc_info=True)
            await ctx.send("❌ Wystąpił nieoczekiwany błąd")

    async def handle_with_confirmation(self, ctx, amount: int, member: discord.Member = None):
        """Obsługa komendy !purge z potwierdzeniem dla dużych liczb"""
        # Dla większych ilości (np. > 50) możesz dodać potwierdzenie
        if amount > 50:
            confirm_msg = await ctx.send(
                f"⚠️ Czy na pewno chcesz usunąć **{amount}** wiadomości?\n"
                f"Odpowiedz `tak` w ciągu 10 sekund aby kontynuować."
            )

            def check_confirm(m):
                return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == 'tak'

            try:
                await self.bot.wait_for('message', timeout=10.0, check=check_confirm)
                await confirm_msg.delete()
                # Kontynuuj z normalnym purge
                await self.handle(ctx, amount, member)
            except asyncio.TimeoutError:
                await confirm_msg.edit(content="❌ Anulowano - brak potwierdzenia.")
                return
        else:
            # Dla małych ilości wykonaj od razu
            await self.handle(ctx, amount, member)