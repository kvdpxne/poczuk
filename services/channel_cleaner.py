"""
Serwis czyszczenia kanałów - Single Responsibility Principle
"""
import discord
from datetime import datetime
from utils.helpers import create_embed
from utils.logger import get_logger


class ChannelCleaner:
    """Odpowiedzialny za czyszczenie kanałów Discord"""

    def __init__(self):
        self.logger = get_logger(__name__)

    async def clean_channel(
        self,
        bot,
        channel_id: int,
        exclude_pinned: bool = True,
        message_limit: int = 0,
        send_confirmation: bool = False
    ) -> int:
        """
        Czyści wiadomości na kanale z opcjami filtrowania

        :param bot: Instancja bota
        :param channel_id: ID kanału do wyczyszczenia
        :param exclude_pinned: Czy pomijać przypięte wiadomości
        :param message_limit: Limit wiadomości do usunięcia (0 = wszystkie)
        :param send_confirmation: Czy wysłać potwierdzenie
        :return: Liczba usuniętych wiadomości
        """
        try:
            channel = bot.get_channel(channel_id)
            if not channel:
                channel = await bot.fetch_channel(channel_id)

            self.logger.info(
                f"Rozpoczynam czyszczenie kanału: {channel.name} ({channel.id}) "
                f"exclude_pinned={exclude_pinned}, limit={message_limit}"
            )

            # Funkcja sprawdzająca dla filtrowania
            def check(message):
                if exclude_pinned and message.pinned:
                    return False
                return True

            # Usuwanie wiadomości z limitem
            limit = None if message_limit == 0 else message_limit
            deleted = await channel.purge(
                limit=limit,
                check=check,
                oldest_first=False
            )
            deleted_count = len(deleted)

            self.logger.info(f"Zakończono czyszczenie: {deleted_count} wiadomości usunięto")

            # Wyślij potwierdzenie jeśli wymagane
            if send_confirmation and deleted_count > 0:
                await self._send_clean_confirmation(channel, deleted_count)
            elif not send_confirmation:
                self.logger.info(f"Pominięto wysyłanie potwierdzenia dla kanału {channel.id}")

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