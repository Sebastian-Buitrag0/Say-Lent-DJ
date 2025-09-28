import discord
from discord.ext import commands

class GeneralCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='help')
    async def help(self, ctx):
        embed = discord.Embed(
            title="🎵 Ayuda de Comandos del Bot de Música",
            description="Aquí tienes una lista de todos los comandos disponibles y lo que hacen.",
            color=discord.Color.purple()
        )

        embed.add_field(
            name="▶️ Comandos Principales",
            value="`!play [nombre/URL]` - Reproduce una canción o la añade a la cola.\n"
                  "`!pause` - Pausa la canción actual.\n"
                  "`!resume` - Reanuda la canción pausada.\n"
                  "`!skip` - Salta a la siguiente canción de la cola.\n"
                  "`!stop` - Detiene la música y limpia la cola.",
            inline=False
        )

        embed.add_field(
            name="📋 Comandos de Gestión de Cola y Canal",
            value="`!queue` - Muestra la cola de canciones actual.\n"
                  "`!clear` - Limpia todas las canciones de la cola.\n"
                  "`!join` - Hace que el bot se una a tu canal de voz.\n"
                  "`!leave` - Desconecta el bot del canal de voz.",
            inline=False
        )
        
        embed.set_footer(text="Recuerda estar en un canal de voz para usar los comandos de música.")

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(GeneralCog(bot))
