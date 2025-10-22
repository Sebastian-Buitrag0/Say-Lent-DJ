import discord
from discord.ext import commands
import yt_dlp
import asyncio

# Opciones para yt-dlp y FFmpeg
YDL_OPTIONS = {'format': 'bestaudio/best', 'noplaylist': 'True'}
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queues = {}
        self.disconnect_timers = {}

    # --- Funciones Auxiliares ---
    def search_yt(self, query):
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
            except Exception:
                return None
        return {'source': info['url'], 'title': info['title']}

    async def play_next(self, ctx):
        if ctx.guild.id in self.queues and self.queues[ctx.guild.id]:
            song = self.queues[ctx.guild.id].pop(0)
            
            # Cancelar temporizador de desconexión si existe
            if ctx.guild.id in self.disconnect_timers:
                self.disconnect_timers[ctx.guild.id].cancel()
                del self.disconnect_timers[ctx.guild.id]
            
            source = discord.FFmpegPCMAudio(song['source'], **FFMPEG_OPTIONS)
            ctx.voice_client.play(source, after=lambda e: self.bot.loop.create_task(self.play_next(ctx)))
            await ctx.send(f"▶️ Ahora reproduciendo: **{song['title']}**")
        else:
            await ctx.send("La cola ha terminado.")
            # Desconectar después de 5 minutos de inactividad
            self.disconnect_timers[ctx.guild.id] = asyncio.create_task(self.auto_disconnect(ctx))

    async def auto_disconnect(self, ctx):
        """Desconecta el bot después de 5 minutos de inactividad"""
        await asyncio.sleep(300)  # 5 minutos
        if ctx.voice_client and not ctx.voice_client.is_playing():
            await ctx.voice_client.disconnect()
            await ctx.send("👋 Me he desconectado por inactividad.")
        if ctx.guild.id in self.disconnect_timers:
            del self.disconnect_timers[ctx.guild.id]

    # --- Checks para comandos ---
    async def cog_check(self, ctx):
        # Todos los comandos en este Cog requieren que el autor esté en un canal de voz
        if not ctx.author.voice:
            await ctx.send("Debes estar en un canal de voz para usar los comandos de música.")
            return False
        return True

    # --- Comandos ---
    @commands.command(name='join')
    async def join(self, ctx):
        channel = ctx.author.voice.channel
        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)
        await channel.connect()
        await ctx.send(f"¡Hola! Me he unido a **{channel}**.")

    @commands.command(name='play')
    async def play(self, ctx, *, query):
        if ctx.voice_client is None:
            await ctx.invoke(self.join)

        song = self.search_yt(query)
        if song is None:
            await ctx.send("No pude encontrar la canción. Intenta con otro nombre.")
            return

        if ctx.guild.id not in self.queues:
            self.queues[ctx.guild.id] = []

        self.queues[ctx.guild.id].append(song)
        
        if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
            await ctx.send(f"✅ Añadido a la cola: **{song['title']}**")
        else:
            await self.play_next(ctx)

    @commands.command(name='pause')
    async def pause(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send("⏸️ Pausado.")
        else:
            await ctx.send("No hay música reproduciéndose en este momento.")

    @commands.command(name='resume')
    async def resume(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send("▶️ Reanudado.")
        else:
            await ctx.send("La música no está pausada.")

    @commands.command(name='skip')
    async def skip(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("⏭️ Canción saltada.")
        else:
            await ctx.send("No hay música que saltar.")

    @commands.command(name='queue')
    async def queue(self, ctx):
        if ctx.guild.id in self.queues and self.queues[ctx.guild.id]:
            queue_list = "\n".join([f"{i+1}. {song['title']}" for i, song in enumerate(self.queues[ctx.guild.id])])
            embed = discord.Embed(title="🎵 Cola de Reproducción", description=queue_list, color=discord.Color.blue())
            await ctx.send(embed=embed)
        else:
            await ctx.send("La cola está vacía.")

    @commands.command(name='clear')
    async def clear(self, ctx):
        if ctx.guild.id in self.queues:
            self.queues[ctx.guild.id].clear()
            await ctx.send("🧹 Cola limpiada.")
        else:
            await ctx.send("La cola ya estaba vacía.")

    @commands.command(name='stop')
    async def stop(self, ctx):
        if ctx.guild.id in self.queues:
            self.queues[ctx.guild.id].clear()
        if ctx.voice_client:
            ctx.voice_client.stop()
        # Cancelar temporizador de desconexión si existe
        if ctx.guild.id in self.disconnect_timers:
            self.disconnect_timers[ctx.guild.id].cancel()
            del self.disconnect_timers[ctx.guild.id]
        await ctx.send("⏹️ Música detenida y cola limpiada.")

    @commands.command(name='leave')
    async def leave(self, ctx):
        if ctx.voice_client:
            # Cancelar temporizador de desconexión si existe
            if ctx.guild.id in self.disconnect_timers:
                self.disconnect_timers[ctx.guild.id].cancel()
                del self.disconnect_timers[ctx.guild.id]
            await ctx.voice_client.disconnect()
            await ctx.send("👋 ¡Adiós!")
        else:
            await ctx.send("No estoy en un canal de voz.")

async def setup(bot):
    await bot.add_cog(MusicCog(bot))
