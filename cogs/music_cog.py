import asyncio
import logging
import discord
from discord.ext import commands
import yt_dlp

YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'default_search': 'auto',
    'quiet': True,
}
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

log = logging.getLogger(__name__)

class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queues = {}
        self.disconnect_timers = {}

    def _cancel_disconnect_timer(self, guild_id):
        timer = self.disconnect_timers.pop(guild_id, None)
        if timer and not timer.done():
            timer.cancel()

    def search_yt(self, query):
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(f"ytsearch1:{query}", download=False)
            if not info['entries']:
                return None
            entry = info['entries'][0]

            audio_url = None
            for fmt in entry.get("formats", []):
                if fmt.get("acodec") != "none":
                    audio_url = fmt["url"]
                    break

            if not audio_url:
                return None
        return {
            'source': audio_url,
            'title': entry['title'],
            'headers': entry.get('http_headers', {}),
        }

    async def _after_track(self, ctx, error):
        if error:
            log.error("Error en reproducción (%s): %s", ctx.guild.id, error)
            await ctx.send("⚠️ Hubo un error con la canción. Intento con la siguiente.")
        await self.play_next(ctx)

    async def play_next(self, ctx):
        queue = self.queues.get(ctx.guild.id, [])
        if queue:
            song = queue.pop(0)
            if not queue:
                self.queues.pop(ctx.guild.id, None)
            self._cancel_disconnect_timer(ctx.guild.id)

            voice_client = ctx.guild.voice_client
            if not voice_client:
                return

            ffmpeg_opts = FFMPEG_OPTIONS.copy()
            headers = song.get('headers')
            if headers:
                header_str = "".join([f"{key}: {value}\r\n" for key, value in headers.items()])
                ffmpeg_opts['before_options'] += f' -headers "{header_str}"'
            
            source = discord.FFmpegPCMAudio(song['source'], **ffmpeg_opts)
            voice_client.play(
                source,
                after=lambda e: asyncio.run_coroutine_threadsafe(
                    self._after_track(ctx, e), self.bot.loop
                )
            )
            await ctx.send(f"▶️ Ahora reproduciendo: **{song['title']}**")
        else:
            voice_client = ctx.guild.voice_client
            if not voice_client:
                self._cancel_disconnect_timer(ctx.guild.id)
                return
            if ctx.guild.id in self.disconnect_timers:
                return
            await ctx.send("La cola ha terminado.")
            self.disconnect_timers[ctx.guild.id] = self.bot.loop.create_task(self.auto_disconnect(ctx))

    async def auto_disconnect(self, ctx):
        try:
            await asyncio.sleep(300)
            voice_client = ctx.guild.voice_client
            if voice_client and not (voice_client.is_playing() or voice_client.is_paused()):
                await voice_client.disconnect()
                await ctx.send("👋 Me he desconectado por inactividad.")
        finally:
            self.disconnect_timers.pop(ctx.guild.id, None)

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

        queue = self.queues.setdefault(ctx.guild.id, [])
        queue.append(song)
        self._cancel_disconnect_timer(ctx.guild.id)

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
        self._cancel_disconnect_timer(ctx.guild.id)
        await ctx.send("⏹️ Música detenida y cola limpiada.")

    @commands.command(name='leave')
    async def leave(self, ctx):
        self._cancel_disconnect_timer(ctx.guild.id)
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send("👋 ¡Adiós!")
        else:
            await ctx.send("No estoy en un canal de voz.")

async def setup(bot):
    await bot.add_cog(MusicCog(bot))
