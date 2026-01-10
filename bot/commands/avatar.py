from datetime import datetime

import discord


class AvatarCommand:

    def __init__(self, bot, logger):
        self.bot = bot
        self.logger = logger

    async def handle(self, ctx, member: discord.Member = None):
        try:
            target = member or ctx.author

            self.logger.info(f"Komenda !avatar wywołana przez {ctx.author} ({ctx.author.id}) dla {target}")

            # Tworzenie embed z avatarem
            embed = discord.Embed(
                title=f"🖼️ Avatar użytkownika {target.display_name}",
                color=target.color if target.color != discord.Color.default() else discord.Color.blue(),
                timestamp=datetime.now()
            )

            embed.set_image(url=target.display_avatar.url)
            embed.add_field(name="Nazwa", value=f"{target.name}#{target.discriminator}", inline=True)
            embed.add_field(name="ID", value=target.id, inline=True)

            # Linki do różnych formatów avatara
            avatar_formats = []
            if target.avatar:
                avatar_formats.append(f"[PNG]({target.avatar.replace(format='png')})")
                avatar_formats.append(f"[JPG]({target.avatar.replace(format='jpg')})")
                avatar_formats.append(f"[WebP]({target.avatar.replace(format='webp')})")
                if target.avatar.is_animated():
                    avatar_formats.append(f"[GIF]({target.avatar.replace(format='gif')})")

            if avatar_formats:
                embed.add_field(name="Formaty", value=" | ".join(avatar_formats), inline=False)

            embed.set_footer(text=f"Żądane przez {ctx.author}", icon_url=ctx.author.display_avatar.url)

            await ctx.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Błąd w komendzie !avatar: {e}", exc_info=True)
            await ctx.send("❌ Wystąpił błąd podczas pobierania avatara")
