from utils import get_logger


class SettleDebtCommand:

    def __init__(self, bot, config_manager, logger=None):
        self.bot = bot
        self.config_manager = config_manager
        self.logger = logger or get_logger(__name__)

    async def handle(self, ctx, debt_id: int):
        """Oznacza dług jako spłacony"""
        try:
            if self.config_manager.settle_debt(debt_id):
                # Zaloguj akcję
                self.config_manager.add_log(
                    user_id=ctx.author.id,
                    guild_id=ctx.guild.id,
                    log_level_name="INFO",
                    action_type_name="SETTLE_DEBT",
                    details=f"Spłacono dług ID: {debt_id}"
                )

                await ctx.send(f"✅ Dług #{debt_id} oznaczony jako spłacony")
            else:
                await ctx.send(f"❌ Nie znaleziono długu #{debt_id}")

        except Exception as e:
            self.logger.error(f"Błąd spłacania długu: {e}", exc_info=True)
            await ctx.send("❌ Wystąpił błąd podczas spłacania długu")