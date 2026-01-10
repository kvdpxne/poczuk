import asyncio

import discord

from utils.helpers import create_embed


class CleanCommand:

    def __init__(self, bot, logger):
        self.bot = bot
        self.logger = logger

    async def handle(self, ctx, amount: int):
        """Główna metoda obsługi komendy"""
        try:
            # Sprawdź uprawnienia
            if not ctx.channel.permissions_for(ctx.author).manage_messages:
                self.logger.warning(f"Brak uprawnień do clean: {ctx.author}")
                await ctx.send("❌ Brak uprawnień! Wymagane: Zarządzanie wiadomościami")
                return

            if not ctx.channel.permissions_for(ctx.guild.me).manage_messages:
                self.logger.warning(f"Bot bez uprawnień do clean na kanale: {ctx.channel.id}")
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
                f"Rozpoczynanie clean (tylko boty): ilość={amount}, "
                f"kanał={ctx.channel.name} ({ctx.channel.id}), "
                f"użytkownik={ctx.author}"
            )

            # Funkcja sprawdzająca - tylko wiadomości od botów
            def is_bot_message(message):
                return message.author.bot

            # Usuń wiadomości
            deleted = await ctx.channel.purge(
                limit=amount + 1,
                check=is_bot_message,
                oldest_first=False
            )

            # Odejmij komendę od liczby (jeśli była usunięta)
            deleted_count = len(deleted) - 1 if ctx.message in deleted else len(deleted)

            # Log zakończenia
            self.logger.info(
                f"Zakończono clean (tylko boty): usunięto={deleted_count} wiadomości, "
                f"kanał={ctx.channel.name} ({ctx.channel.id})"
            )

            # Wyślij potwierdzenie
            embed = create_embed(
                title="🤖 Wiadomości botów wyczyszczone",
                description=f"Usunięto **{deleted_count}** wiadomości od botów",
                color=discord.Color.green(),
            )

            embed.add_field(name="Filtr", value="Tylko wiadomości od botów", inline=False)
            embed.add_field(name="Kanał", value=ctx.channel.mention, inline=True)
            embed.add_field(name="Przez", value=ctx.author.mention, inline=True)

            # Dodaj statystykę jeśli coś usunięto
            if deleted_count > 0:
                # Policz które boty zostały wyczyszczone
                bot_counts = {}
                for msg in deleted:
                    if msg.author != self.bot.user:  # Pomijamy własną komendę
                        bot_name = msg.author.display_name
                        bot_counts[bot_name] = bot_counts.get(bot_name, 0) + 1

                if bot_counts:
                    bots_list = "\n".join([f"• **{bot}**: {count} wiad." for bot, count in bot_counts.items()])
                    embed.add_field(name="👥 Usunięte boty", value=bots_list, inline=False)

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
            self.logger.error(f"Błąd HTTP podczas clean: {e}")
            await ctx.send(f"❌ Błąd podczas usuwania wiadomości botów: {e}")
        except Exception as e:
            self.logger.error(f"Nieoczekiwany błąd w clean: {e}", exc_info=True)
            await ctx.send("❌ Wystąpił nieoczekiwany błąd")

    async def handle_with_confirmation(self, ctx, amount: int):
        """Obsługa komendy !clean z potwierdzeniem dla dużych liczb"""
        # Dla większych ilości (np. > 50) dodaj potwierdzenie
        if amount > 50:
            confirm_msg = await ctx.send(
                f"⚠️ Czy na pewno chcesz usunąć **{amount}** wiadomości od botów?\n"
                f"Ta akcja usunie **tylko** wiadomości od botów.\n"
                f"Odpowiedz `tak` w ciągu 10 sekund aby kontynuować."
            )

            def check_confirm(m):
                return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == 'tak'

            try:
                await self.bot.wait_for('message', timeout=10.0, check=check_confirm)
                await confirm_msg.delete()
                # Kontynuuj z normalnym clean
                await self.handle(ctx, amount)
            except asyncio.TimeoutError:
                await confirm_msg.edit(content="❌ Anulowano - brak potwierdzenia.")
                return
        else:
            # Dla małych ilości wykonaj od razu
            await self.handle(ctx, amount)
