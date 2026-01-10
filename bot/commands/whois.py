import discord

from utils.helpers import create_embed


class WhoisCommand:

    def __init__(self, bot, logger):
        self.bot = bot
        self.logger = logger

    async def handle(self, ctx, member: discord.Member = None):
        try:
            target = member or ctx.author

            self.logger.info(f"Komenda !whois wywołana przez {ctx.author} ({ctx.author.id}) dla {target}")

            # Tworzenie szczegółowego embed
            embed = create_embed(
                title=f"👤 Informacje o {target.display_name}",
                color=target.color if target.color != discord.Color.default() else discord.Color.purple(),
                description=""
            )

            # Ustaw avatar
            embed.set_thumbnail(url=target.display_avatar.url)

            # Podstawowe informacje
            embed.add_field(name="📝 Nazwa", value=f"{target.name}#{target.discriminator}", inline=True)
            embed.add_field(name="🆔 ID", value=target.id, inline=True)
            embed.add_field(name="🤖 Bot", value="Tak" if target.bot else "Nie", inline=True)

            # Daty
            embed.add_field(
                name="📅 Konto utworzone",
                value=f"<t:{int(target.created_at.timestamp())}:F>\n(<t:{int(target.created_at.timestamp())}:R>)",
                inline=False
            )

            if isinstance(target, discord.Member):
                embed.add_field(
                    name="📅 Dołączył do serwera",
                    value=f"<t:{int(target.joined_at.timestamp())}:F>\n(<t:{int(target.joined_at.timestamp())}:R>)",
                    inline=False
                )

                # Role
                roles = [role.mention for role in target.roles[1:]]  # Pomijaj @everyone
                if roles:
                    roles_text = " ".join(roles[-10:])  # Ostatnie 10 ról
                    if len(roles) > 10:
                        roles_text += f"\n...i {len(roles) - 10} więcej"
                    embed.add_field(name=f"🎭 Role ({len(roles)})", value=roles_text, inline=False)
                else:
                    embed.add_field(name="🎭 Role", value="Brak ról", inline=False)

                # Najwyższa rola
                if target.top_role and target.top_role != ctx.guild.default_role:
                    embed.add_field(name="👑 Najwyższa rola", value=target.top_role.mention, inline=True)

                # Administrator
                embed.add_field(name="⚙️ Administrator",
                                value="Tak" if target.guild_permissions.administrator else "Nie", inline=True)

                # Status
                status_emoji = {
                    'online': '🟢',
                    'idle': '🟡',
                    'dnd': '🔴',
                    'offline': '⚫'
                }
                embed.add_field(
                    name="📱 Status",
                    value=f"{status_emoji.get(str(target.status), '❓')} {str(target.status).upper()}",
                    inline=True
                )

                # Aktywność
                if target.activity:
                    activity_type = str(target.activity.type).split('.')[-1].title()
                    embed.add_field(name="🎮 Aktywność", value=f"{activity_type}: {target.activity.name}", inline=False)

            # Booster
            if hasattr(target, 'premium_since') and target.premium_since:
                embed.add_field(
                    name="🌟 Booster",
                    value=f"Od <t:{int(target.premium_since.timestamp())}:R>",
                    inline=True
                )

            embed.set_footer(text=f"Żądane przez {ctx.author}", icon_url=ctx.author.display_avatar.url)

            await ctx.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Błąd w komendzie !whois: {e}", exc_info=True)
            await ctx.send("❌ Wystąpił błąd podczas pobierania informacji o użytkowniku")
