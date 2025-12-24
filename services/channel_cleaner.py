"""
Serwis czyszczenia kanałów
"""
import discord
from datetime import datetime
from utils.helpers import create_embed


class ChannelCleaner:
    """Odpowiedzialny za czyszczenie kanałów Discord"""
    
    async def clean_channel(self, bot, channel_id: int) -> int:
        """
        Czyści wszystkie wiadomości na kanale
        Zwraca liczbę usuniętych wiadomości
        """
        try:
            channel = bot.get_channel(channel_id)
            if not channel:
                channel = await bot.fetch_channel(channel_id)
            
            print(f"[{datetime.now()}] Czyszczenie kanału {channel.name}...")
            
            # Usuwa wszystkie wiadomości
            deleted = await channel.purge(limit=None, oldest_first=False)
            deleted_count = len(deleted)
            
            print(f"  Usunięto {deleted_count} wiadomości")
            
            # Wyślij potwierdzenie na kanale
            await self._send_clean_confirmation(channel, deleted_count)
            
            return deleted_count
            
        except discord.Forbidden:
            print(f"  BRAK UPRAWNIEŃ dla kanału {channel_id}")
            return 0
        except discord.HTTPException as e:
            print(f"  Błąd HTTP: {e}")
            return 0
        except Exception as e:
            print(f"  Nieznany błąd: {e}")
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
