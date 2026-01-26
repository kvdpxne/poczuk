from decimal import Decimal

import discord

from models.debt import Debt
from utils import get_logger
from utils.helpers import create_embed


class AddDebtCommand:

    def __init__(self, bot, config_manager, logger=None):
        self.bot = bot
        self.config_manager = config_manager
        self.logger = logger or get_logger(__name__)

    async def handle(
        self,
        ctx,
        debtor: discord.Member,
        creditor: discord.Member,
        amount: Decimal,
        description: str = "",
        currency: str = "PLN"
    ):
        """Dodaje nowy dług"""
        try:
            # Walidacja
            if amount <= 0:
                await ctx.send("❌ Kwota musi być większa od 0")
                return

            if debtor == creditor:
                await ctx.send("❌ Nie można dodać długu do samego siebie")
                return

            # Sprawdź czy dług już istnieje (niezapłacony)
            existing_debts = self.config_manager.get_debts(
                guild_id=ctx.guild.id,
                debtor_id=debtor.id,
                creditor_id=creditor.id,
                is_settled=False
            )

            if existing_debts:
                existing_amount = sum(debt.amount for debt in existing_debts)
                embed = create_embed(
                    title="ℹ️ Istniejące długi",
                    description=f"{debtor.mention} już jest winien {creditor.mention} {existing_amount} {currency}",
                    color=discord.Color.orange()
                )
                embed.add_field(name="Czy dodać nowy dług?", value="Odpowiedz `tak` w ciągu 30 sekund", inline=False)
                await ctx.send(embed=embed)

                def check(m):
                    return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == 'tak'

                try:
                    await self.bot.wait_for('message', timeout=30.0, check=check)
                except:
                    await ctx.send("❌ Anulowano dodawanie długu")
                    return

            # Stwórz nowy dług
            debt = Debt(
                debtor_id=debtor.id,
                creditor_id=creditor.id,
                amount=amount,
                currency=currency,
                description=description,
                guild_id=ctx.guild.id
            )

            if self.config_manager.add_debt(debt):
                # Zaloguj akcję
                self.config_manager.add_log(
                    user_id=ctx.author.id,
                    guild_id=ctx.guild.id,
                    log_level_name="INFO",
                    action_type_name="ADD_DEBT",
                    details=f"Dodano dług: {debtor} → {creditor}: {amount} {currency}"
                )

                embed = create_embed(
                    title="✅ Dług dodany",
                    description=f"{debtor.mention} jest winien {creditor.mention}",
                    color=discord.Color.green()
                )
                embed.add_field(name="Kwota", value=f"{amount} {currency}", inline=True)
                if description:
                    embed.add_field(name="Opis", value=description, inline=True)
                embed.add_field(name="ID długu", value=str(debt.debt_id), inline=True)
                embed.set_footer(text=f"Dodane przez {ctx.author}")

                await ctx.send(embed=embed)
            else:
                await ctx.send("❌ Nie udało się dodać długu")

        except ValueError:
            await ctx.send("❌ Nieprawidłowa kwota. Użyj formatu np. 100.50")
        except Exception as e:
            self.logger.error(f"Błąd dodawania długu: {e}", exc_info=True)
            await ctx.send("❌ Wystąpił błąd podczas dodawania długu")