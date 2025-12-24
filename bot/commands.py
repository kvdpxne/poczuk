"""
Komendy bota
"""
import discord
from discord.ext import commands
from models.channel_schedule import ChannelSchedule
from utils.validators import TimeValidator
from utils.helpers import create_embed, format_channel_mention, get_current_datetime


class CommandHandler:
    """Obsługa komend bota"""
    
    def __init__(self, bot, config_manager, scheduler):
        self.bot = bot
        self.config_manager = config_manager
        self.scheduler = scheduler
        self.validator = TimeValidator()
    
    async def handle_add(self, ctx, channel: discord.TextChannel, clean_time: str):
        """Obsługuje komendę !add"""
        # Walidacja czasu
        if not self.validator.validate_time_format(clean_time):
            return await ctx.send("❌ Nieprawidłowy format czasu. Użyj HH:MM (np. 03:00)")
        
        # Sprawdź czy kanał już ma harmonogram
        existing = self.config_manager.get_schedule(channel.id)
        if existing:
            return await ctx.send(
                f"❌ Kanał {channel.mention} już ma ustawione czyszczenie o {existing.time}"
            )
        
        # Utwórz nowy harmonogram
        new_schedule = ChannelSchedule(
            channel_id=channel.id,
            channel_name=channel.name,
            time=clean_time,
            added_by=ctx.author.id,
            added_at=get_current_datetime()
        )
        
        # Zapisz harmonogram
        if self.config_manager.add_schedule(new_schedule):
            embed = create_embed(
                title="✅ Harmonogram dodany",
                description=f"Kanał {channel.mention} będzie czyszczony codziennie o **{clean_time}**",
                color=discord.Color.green()
            )
            embed.add_field(name="ID kanału", value=str(channel.id))
            embed.add_field(
                name="Liczba harmonogramów", 
                value=str(len(self.config_manager.load_schedules()))
            )
            embed.set_footer(text=f"Dodane przez {ctx.author}")
            
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ Nie udało się dodać harmonogramu")
    
    async def handle_remove(self, ctx, channel: discord.TextChannel):
        """Obsługuje komendę !remove"""
        if self.config_manager.remove_schedule(channel.id):
            embed = create_embed(
                title="🗑️ Harmonogram usunięty",
                description=f"Usunięto harmonogram czyszczenia dla {channel.mention}",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"❌ Nie znaleziono harmonogramu dla {channel.mention}")
    
    async def handle_list(self, ctx):
        """Obsługuje komendę !list"""
        schedules = self.config_manager.load_schedules()
        
        if not schedules:
            embed = create_embed(
                title="📋 Harmonogramy czyszczenia",
                description="Brak aktywnych harmonogramów",
                color=discord.Color.blue()
            )
        else:
            embed = create_embed(
                title="📋 Harmonogramy czyszczenia",
                description=f"Liczba aktywnych harmonogramów: {len(schedules)}",
                color=discord.Color.blue()
            )
            
            for schedule in schedules:
                channel_mention = format_channel_mention(self.bot, schedule.channel_id)
                
                embed.add_field(
                    name=f"⏰ {schedule.time}",
                    value=f"Kanał: {channel_mention}\nID: {schedule.channel_id}",
                    inline=False
                )
        
        await ctx.send(embed=embed)
    
    async def handle_test(self, ctx, channel: discord.TextChannel = None):
        """Obsługuje komendę !test"""
        target_channel = channel or ctx.channel
        
        embed = create_embed(
            title="🧪 Test czyszczenia",
            description=f"Rozpoczynam testowe czyszczenie {target_channel.mention}...",
            color=discord.Color.yellow()
        )

        msg = await ctx.send(embed=embed) 
        deleted_count = await self.scheduler.execute_test_clean(target_channel.id)
        
        embed = create_embed(
            title="✅ Test zakończony",
            description=f"Usunięto {deleted_count} wiadomości z {target_channel.mention}",
            color=discord.Color.green()
        )

        try:
            await msg.edit(embed=embed)
        except discord.NotFound:
            # Jeśli wiadomość została usunięta podczas czyszczenia, wyślij nową
            await ctx.send(embed=embed)
    
    async def handle_help(self, ctx):
        """Obsługuje komendę !help"""
        embed = create_embed(
            title="🤖 Discord Cleaner - Pomoc",
            description="Bot do automatycznego czyszczenia kanałów",
            color=discord.Color.purple()
        )
        
        commands_info = [
            ("$add #kanał HH:MM", "Dodaje codzienne czyszczenie kanału\nPrzykład: `!add #ogólne 03:00`"),
            ("$remove #kanał", "Usuwa harmonogram czyszczenia kanału"),
            ("$list", "Wyświetla wszystkie harmonogramy"),
            ("$test [#kanał]", "Testowe czyszczenie (opcjonalnie: inny kanał)"),
            ("$help", "Wyświetla tę wiadomość")
        ]
        
        for cmd, desc in commands_info:
            embed.add_field(name=cmd, value=desc, inline=False)
        
        embed.set_footer(text="Wymagane uprawnienia: Administrator")
        
        await ctx.send(embed=embed)
    
    async def handle_status(self, ctx):
        """Obsługuje komendę !status"""
        import psutil
        import os
        
        # Statystyki bota
        schedules = self.config_manager.load_schedules()
        uptime = get_current_datetime() - self.bot.start_time
        
        embed = create_embed(
            title="📊 Status bota",
            description="",
            color=discord.Color.blue()
        )
        
        embed.add_field(name="⏱️ Uptime", value=str(uptime).split('.')[0])
        embed.add_field(name="📋 Harmonogramy", value=len(schedules))
        embed.add_field(name="🏠 Serwery", value=len(self.bot.guilds))
        
        # Statystyki systemowe
        process = psutil.Process(os.getpid())
        memory_mb = process.memory_info().rss / 1024 / 1024
        
        embed.add_field(name="💾 RAM", value=f"{memory_mb:.1f} MB")
        embed.add_field(name="📶 Ping", value=f"{round(self.bot.latency * 1000)}ms")
        embed.add_field(name="👤 Użytkownicy", value=sum(g.member_count for g in self.bot.guilds))
        
        await ctx.send(embed=embed)
