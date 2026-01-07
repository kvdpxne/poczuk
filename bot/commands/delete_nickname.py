"""
Moduł komendy !flipcoin
"""
import discord

from utils.helpers import create_embed


class DeleteNicknameCommand:
    """Obsługa komendy !flipcoin"""

    def __init__(self, bot, logger):
        self.bot = bot
        self.logger = logger

    async def handle(self, ctx, member: discord.Member):
        """Obsługuje komendę !clearnick - usuwa niestandardowy nick użytkownika"""
        try:
            # Sprawdź uprawnienia
            if not ctx.author.guild_permissions.manage_nicknames:
                self.logger.warning(f"Brak uprawnień do clearnick: {ctx.author}")
                await ctx.send("❌ Brak uprawnień! Wymagane: Zarządzanie nickami")
                return

            if not ctx.guild.me.guild_permissions.manage_nicknames:
                self.logger.warning(f"Bot bez uprawnień do clearnick na serwerze: {ctx.guild.id}")
                await ctx.send("❌ Bot nie ma uprawnień do zarządzania nickami")
                return

            # Sprawdź czy to zmiana nicku bota samego siebie
            is_bot_self_change = member.id == ctx.guild.me.id

            # Jeśli to nie bot zmienia swój własny nick, sprawdź hierarchię ról
            if not is_bot_self_change and member.top_role >= ctx.guild.me.top_role:
                self.logger.warning(f"Próba usunięcia nicku wyżej postawionego użytkownika: {member}")
                await ctx.send("❌ Nie mogę zmienić nicku użytkownikowi z wyższą lub równą rolą")
                return

            # Sprawdź czy użytkownik ma niestandardowy nick
            if member.nick is None:
                await ctx.send(f"ℹ️ Użytkownik {member.mention} już używa swojej oryginalnej nazwy (`{member.name}`)")
                return

            old_nick = member.nick

            # Usuń nick (ustaw na None)
            await member.edit(nick=None)

            self.logger.info(
                f"Usunięto nick: {member.name} ({member.id}) z '{old_nick}' na domyślny przez {ctx.author}")

            embed = create_embed(
                title="✅ Nick usunięty",
                description=f"Usunięto niestandardowy nick użytkownika {member.mention}",
                color=discord.Color.green()
            )

            embed.add_field(name="Użytkownik", value=f"{member.mention}\n`{member.name}#{member.discriminator}`",
                            inline=False)
            embed.add_field(name="Stary nick", value=old_nick, inline=True)
            embed.add_field(name="Nowy nick", value=f"`{member.name}` (domyślny)", inline=True)
            embed.add_field(name="Usunięty przez", value=ctx.author.mention, inline=True)

            # Dodaj specjalną notatkę jeśli zmieniono nick bota
            if is_bot_self_change:
                embed.add_field(name="ℹ️ Uwaga", value="Został usunięty nick bota", inline=False)

            await ctx.send(embed=embed)

        except discord.Forbidden:
            if member.id == ctx.guild.me.id:
                self.logger.error(f"Brak uprawnień do zmiany własnego nicku bota")
                await ctx.send("❌ Bot nie ma uprawnień do zmiany własnego nicku. Wymagane: 'Zarządzanie nickami'")
            else:
                self.logger.error(f"Brak uprawnień do usunięcia nicku użytkownika {member.id}")
                await ctx.send(
                    "❌ Brak uprawnień do usunięcia nicku. Upewnij się, że bot ma wyższą rolę niż użytkownik.")
        except discord.HTTPException as e:
            self.logger.error(f"Błąd HTTP podczas usuwania nicku: {e}")
            await ctx.send(f"❌ Błąd podczas usuwania nicku: {e}")
        except Exception as e:
            self.logger.error(f"Nieoczekiwany błąd w clearnick: {e}", exc_info=True)
            await ctx.send("❌ Wystąpił nieoczekiwany błąd podczas usuwania nicku")
