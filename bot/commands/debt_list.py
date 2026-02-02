import discord

from utils import get_logger
from utils.helpers import create_embed


class ListDebtCommand:

    def __init__(self, bot, config_manager, logger=None):
        self.bot = bot
        self.config_manager = config_manager
        self.logger = logger or get_logger(__name__)

    async def handle(self, ctx, member: discord.Member = None, show_settled: bool = False):
        """Wyświetla listę długów w najprostszej formie"""
        try:
            guild_id = ctx.guild.id

            # Pobierz długi
            if member:
                # Długi członka jako dłużnika
                debts_as_debtor = self.config_manager.get_debts(
                    guild_id=guild_id,
                    debtor_id=member.id,
                    is_settled=False if not show_settled else None
                )
                # Długi członka jako wierzyciela
                debts_as_creditor = self.config_manager.get_debts(
                    guild_id=guild_id,
                    creditor_id=member.id,
                    is_settled=False if not show_settled else None
                )
                debts = debts_as_debtor + debts_as_creditor
                title = f"💰 Długi {member.display_name}"
            else:
                # Wszystkie długi na serwerze
                debts = self.config_manager.get_debts(
                    guild_id=guild_id,
                    is_settled=False if not show_settled else None
                )
                title = f"💰 Długi na serwerze"

            if not debts:
                embed = create_embed(
                    title=title,
                    description="Brak długów" if not show_settled else "Brak długów (w tym spłaconych)",
                    color=discord.Color.blue()
                )
                await ctx.send(embed=embed)
                return

            # Grupuj długi według pary (dłużnik → wierzyciel)
            debt_summary = {}
            debt_details = {}

            for debt in debts:
                key = (debt.debtor_id, debt.creditor_id)

                # Dodaj do sumy całkowitej
                if key not in debt_summary:
                    debt_summary[key] = debt.amount
                else:
                    debt_summary[key] += debt.amount

                # Zapisz szczegóły poszczególnych długów
                if key not in debt_details:
                    debt_details[key] = []

                debt_details[key].append(debt)

            # Utwórz embed z prostym widokiem
            embed = create_embed(
                title=title,
                description=f"Liczba długów: {len(debts)} | Pary: {len(debt_summary)}",
                color=discord.Color.blue()
            )

            # Dodaj sekcję "KTO jest ILE WINNY dla KOGO"
            summary_text = ""
            for (debtor_id, creditor_id), total_amount in debt_summary.items():
                debtor = ctx.guild.get_member(debtor_id)
                creditor = ctx.guild.get_member(creditor_id)

                debtor_name = debtor.mention if debtor else f"ID:{debtor_id}"
                creditor_name = creditor.mention if creditor else f"ID:{creditor_id}"

                # Formatuj kwotę
                currency = next(
                    (d.currency for d in debts if d.debtor_id == debtor_id and d.creditor_id == creditor_id), "PLN")

                summary_text += f"**{debtor_name}** → **{creditor_name}**: {total_amount:.2f} {currency}\n"

            embed.add_field(
                name="📊 PODSUMOWANIE: KTO → KOMU ILE",
                value=summary_text or "Brak danych",
                inline=False
            )

            # Dodaj sekcję ze szczegółami (tylko jeśli mniej niż 10 par)
            if len(debt_details) <= 10:
                details_text = ""
                for (debtor_id, creditor_id), debts_list in debt_details.items():
                    debtor = ctx.guild.get_member(debtor_id)
                    creditor = ctx.guild.get_member(creditor_id)

                    debtor_name = debtor.mention if debtor else f"ID:{debtor_id}"
                    creditor_name = creditor.mention if creditor else f"ID:{creditor_id}"

                    details_text += f"\n**{debtor_name} → {creditor_name}:**\n"

                    for i, debt in enumerate(debts_list, 1):
                        status = "✅ " if debt.is_settled else "❌ "
                        description = f" ({debt.description[:30]}...)" if debt.description and len(
                            debt.description) > 30 else f" ({debt.description})" if debt.description else ""
                        details_text += f"  {debt.debt_id}. {status}{debt.amount:.2f} {debt.currency}{description}\n"

                if details_text:
                    embed.add_field(
                        name="📋 SZCZEGÓŁY: Poszczególne długi",
                        value=details_text[:1000],  # Limit Discord
                        inline=False
                    )

            await ctx.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Błąd listowania długów: {e}", exc_info=True)
            await ctx.send("❌ Wystąpił błąd podczas pobierania listy długów")