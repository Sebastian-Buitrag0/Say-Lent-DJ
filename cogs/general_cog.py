import discord
from discord.ext import commands

class GeneralCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='help')
    async def help(self, ctx):
        embed = discord.Embed(
            title="🎶 ¡Bienvenido a Say-Lent DJ!",
            description=(
                "Usa estos comandos para controlar la música en tu servidor.\n"
                "Para reproducir algo rápidamente: **`!play <canción o URL>`**"
            ),
            color=discord.Color.from_rgb(138, 43, 226)
        )
        embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/727/727269.png")
        embed.add_field(
            name="▶️ Reproducción",
            value=(
                "`!play <nombre/URL>` — Reproduce o agrega a la cola\n"
                "`!pause` — Pausa la pista actual\n"
                "`!resume` — Reanuda la reproducción\n"
                "`!skip` — Salta a la siguiente canción\n"
                "`!stop` — Detiene todo y limpia la cola"
            ),
            inline=False
        )
        embed.add_field(
            name="📋 Gestión de Cola",
            value=(
                "`!queue` — Muestra las canciones en espera\n"
                "`!clear` — Vacía la cola completa\n"
                "`!remove <posición>` — Quita una canción específica"
            ),
            inline=False
        )
        embed.add_field(
            name="🔊 Voz",
            value=(
                "`!join` — El bot se une a tu voz\n"
                "`!leave` — Se desconecta del canal\n"
                "`!np` — Muestra la canción actual"
            ),
            inline=False
        )
        embed.set_footer(text="Recuerda estar en un canal de voz antes de usar los comandos musicales.")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(GeneralCog(bot))
