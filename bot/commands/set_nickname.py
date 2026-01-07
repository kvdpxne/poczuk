"""
Moduł komendy !flipcoin
"""
import random
import discord
from datetime import datetime
from utils.helpers import create_embed


class SetNicknameCommand:
    """Obsługa komendy !flipcoin"""

    def __init__(self, bot, logger):
        self.bot = bot
        self.logger = logger

    async def handle(self, ctx, member: discord.Member, nickname: str):
        """Obsługuje komendę !setnick - zmienia nick użytkownika"""
        try:
            # Sprawdź uprawnienia
            if not ctx.author.guild_permissions.manage_nicknames:
                self.logger.warning(f"Brak uprawnień do setnick: {ctx.author}")
                await ctx.send("❌ Brak uprawnień! Wymagane: Zarządzanie nickami")
                return

            if not ctx.guild.me.guild_permissions.manage_nicknames:
                self.logger.warning(f"Bot bez uprawnień do setnick na serwerze: {ctx.guild.id}")
                await ctx.send("❌ Bot nie ma uprawnień do zarządzania nickami")
                return

            # Sprawdź czy to zmiana nicku bota samego siebie
            is_bot_self_change = member.id == ctx.guild.me.id

            # Jeśli to nie bot zmienia swój własny nick, sprawdź hierarchię ról
            if not is_bot_self_change and member.top_role >= ctx.guild.me.top_role:
                self.logger.warning(f"Próba zmiany nicku wyżej postawionego użytkownika: {member}")
                await ctx.send("❌ Nie mogę zmienić nicku użytkownikowi z wyższą lub równą rolą")
                return

            # Sprawdź długość nicku
            if len(nickname) > 32:
                await ctx.send("❌ Nick nie może być dłuższy niż 32 znaki (ograniczenie Discorda)")
                return

            # Sprawdź czy nick zawiera niedozwolone znaki
            if nickname.strip() == "":
                await ctx.send("❌ Nick nie może być pusty")
                return

            old_nick = member.display_name
            old_nick_actual = member.nick or "Brak (używa nazwy użytkownika)"

            # Zmień nick
            await member.edit(nick=nickname)

            self.logger.info(
                f"Zmieniono nick: {member.name} ({member.id}) z '{old_nick}' na '{nickname}' przez {ctx.author}")

            embed = create_embed(
                title="✅ Nick zmieniony",
                description=f"Pomyślnie zmieniono nick użytkownika {member.mention}",
                color=discord.Color.green()
            )

            embed.add_field(name="Użytkownik", value=f"{member.mention}\n`{member.name}#{member.discriminator}`",
                            inline=False)
            embed.add_field(name="Stary nick", value=old_nick_actual, inline=True)
            embed.add_field(name="Nowy nick", value=nickname, inline=True)
            embed.add_field(name="Zmieniony przez", value=ctx.author.mention, inline=True)

            # Dodaj specjalną notatkę jeśli zmieniono nick bota
            if is_bot_self_change:
                embed.add_field(name="ℹ️ Uwaga", value="Został zmieniony nick bota", inline=False)

            await ctx.send(embed=embed)

        except discord.Forbidden:
            if member.id == ctx.guild.me.id:
                self.logger.error(f"Brak uprawnień do zmiany własnego nicku bota")
                await ctx.send("❌ Bot nie ma uprawnień do zmiany własnego nicku. Wymagane: 'Zarządzanie nickami'")
            else:
                self.logger.error(f"Brak uprawnień do zmiany nicku użytkownika {member.id}")
                await ctx.send("❌ Brak uprawnień do zmiany nicku. Upewnij się, że bot ma wyższą rolę niż użytkownik.")
        except discord.HTTPException as e:
            self.logger.error(f"Błąd HTTP podczas zmiany nicku: {e}")
            await ctx.send(f"❌ Błąd podczas zmiany nicku: {e}")
        except Exception as e:
            self.logger.error(f"Nieoczekiwany błąd w setnick: {e}", exc_info=True)
            await ctx.send("❌ Wystąpił nieoczekiwany błąd podczas zmiany nicku")