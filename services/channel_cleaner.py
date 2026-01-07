"""
Serwis czyszczenia kanałów - Single Responsibility Principle
"""
import discord

from utils.helpers import create_embed
from utils.logger import get_module_logger


class ChannelCleaner:
    """Odpowiedzialny za czyszczenie kanałów Discord"""

    def __init__(self):
        self.logger = get_module_logger(__name__)

    async def clean_channel(self, bot, channel_id: int) -> int:
        """
        Czyści wszystkie wiadomości na kanale
        Zwraca liczbę usuniętych wiadomości
        """
        try:
            channel = bot.get_channel(channel_id)
            if not channel:
                channel = await bot.fetch_channel(channel_id)

            self.logger.info(f"Rozpoczynam czyszczenie kanału: {channel.name} ({channel.id})")

            # Usuwa wszystkie wiadomości
            deleted = await channel.purge(limit=None, oldest_first=False)
            deleted_count = len(deleted)

            self.logger.info(f"Zakończono czyszczenie: {deleted_count} wiadomości usunięto")

            # Wyślij potwierdzenie na kanale
            await self._send_clean_confirmation(channel, deleted_count)

            return deleted_count

        except discord.Forbidden:
            self.logger.error(f"Brak uprawnień do czyszczenia kanału {channel_id}")
            return 0
        except discord.HTTPException as e:
            self.logger.error(f"Błąd HTTP podczas czyszczenia kanału {channel_id}: {e}")
            return 0
        except Exception as e:
            self.logger.error(f"Nieoczekiwany błąd podczas czyszczenia kanału {channel_id}: {e}", exc_info=True)
            return 0

    async def _send_clean_confirmation(self, channel, deleted_count: int):
        """Wysyła potwierdzenie czyszczenia na kanał"""
        embed = create_embed(
            title="🧹 Kanał wyczyszczony",
            description=f"Usunięto {deleted_count} wiadomości",
            color=discord.Color.green()
        )
        embed.set_footer(text="Automatyczne czyszczenie")

        await channel.send(embed=embed)
