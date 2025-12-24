"""
Funkcje pomocnicze
"""
import discord
from datetime import datetime


def create_embed(title: str, description: str, color: discord.Color) -> discord.Embed:
    """Tworzy osadzoną wiadomość - DRY (Don't Repeat Yourself)"""
    embed = discord.Embed(
        title=title,
        description=description,
        color=color,
        timestamp=datetime.now()
    )
    return embed


def format_channel_mention(bot, channel_id: int) -> str:
    """Formatuje mention kanału lub zwraca jego ID"""
    channel = bot.get_channel(channel_id)
    return channel.mention if channel else f"ID: {channel_id}"


def get_current_datetime() -> datetime:
    """Zwraca aktualną datę i czas"""
    return datetime.now()
