import discord
from discord.ext import commands
import yt_dlp
import asyncio
from config import DISCORD_TOKEN

# --- Configuración Inicial ---
# Define los intentos (intents) que tu bot necesita.
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

# Desactivamos el comando help por defecto para crear el nuestro.
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# Opciones para yt-dlp y FFmpeg
YDL_OPTIONS = {'format': 'bestaudio/best', 'noplaylist': 'True'}
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

# Diccionario para almacenar las colas de música de cada servidor (guild).
queues = {}

# --- Funciones Auxiliares ---

def search_yt(query):
    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
        try:
            info = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
        except Exception:
            return None
    return {'source': info['url'], 'title': info['title']}

async def play_next(ctx):
    if ctx.guild.id in queues and queues[ctx.guild.id]:
        song = queues[ctx.guild.id].pop(0)
        source = discord.FFmpegPCMAudio(song['source'], **FFMPEG_OPTIONS)
        ctx.voice_client.play(source, after=lambda _: bot.loop.create_task(play_next(ctx)))
        await ctx.send(f"▶️ Ahora reproduciendo: **{song['title']}**")
    else:
        await ctx.send("La cola ha terminado.")

# --- Eventos del Bot ---

@bot.event
async def on_ready():
    print(f'✅ Bot conectado como {bot.user}')
    await bot.change_presence(activity=discord.Game(name="música | !help"))

# --- Comandos del Bot ---

# ¡NUEVO COMANDO DE AYUDA!
@bot.command(name='help')
async def help(ctx):
    embed = discord.Embed(
        title="🎵 Ayuda de Comandos del Bot de Música",
        description="Aquí tienes una lista de todos los comandos disponibles y lo que hacen.",
        color=discord.Color.purple() # Puedes cambiar el color
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


@bot.command(name='join')
async def join(ctx):
    if not ctx.author.voice:
        await ctx.send("No estás conectado a un canal de voz.")
        return
    channel = ctx.author.voice.channel
    await channel.connect()
    await ctx.send(f"¡Hola! Me he unido a **{channel}**.")

@bot.command(name='play')
async def play(ctx, *, query):
    if not ctx.author.voice:
        await ctx.send("Debes estar en un canal de voz para usar este comando.")
        return
    if ctx.voice_client is None:
        await ctx.author.voice.channel.connect()

    song = search_yt(query)
    if song is None:
        await ctx.send("No pude encontrar la canción. Intenta con otro nombre.")
        return

    if ctx.guild.id not in queues:
        queues[ctx.guild.id] = []

    if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
        queues[ctx.guild.id].append(song)
        await ctx.send(f"✅ Añadido a la cola: **{song['title']}**")
    else:
        queues[ctx.guild.id].append(song) # Añadimos la primera canción a la cola también
        await play_next(ctx) # Llamamos a play_next para iniciar la reproducción

@bot.command(name='pause')
async def pause(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("⏸️ Pausado.")
    else:
        await ctx.send("No hay música reproduciéndose en este momento.")

@bot.command(name='resume')
async def resume(ctx):
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("▶️ Reanudado.")
    else:
        await ctx.send("La música no está pausada.")

@bot.command(name='skip')
async def skip(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("⏭️ Canción saltada.")
    else:
        await ctx.send("No hay música que saltar.")

@bot.command(name='queue')
async def queue(ctx):
    if ctx.guild.id in queues and queues[ctx.guild.id]:
        queue_list = "\n".join([f"{i+1}. {song['title']}" for i, song in enumerate(queues[ctx.guild.id])])
        embed = discord.Embed(title="🎵 Cola de Reproducción", description=queue_list, color=discord.Color.blue())
        await ctx.send(embed=embed)
    else:
        await ctx.send("La cola está vacía.")

@bot.command(name='clear')
async def clear(ctx):
    if ctx.guild.id in queues:
        queues[ctx.guild.id].clear()
        await ctx.send("🧹 Cola limpiada.")
    else:
        await ctx.send("La cola ya estaba vacía.")

@bot.command(name='stop')
async def stop(ctx):
    if ctx.guild.id in queues:
        queues[ctx.guild.id].clear()
    if ctx.voice_client and (ctx.voice_client.is_playing() or ctx.voice_client.is_paused()):
        ctx.voice_client.stop()
        await ctx.send("⏹️ Música detenida y cola limpiada.")
    else:
        await ctx.send("No hay nada que detener.")

@bot.command(name='leave')
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 ¡Adiós!")
    else:
        await ctx.send("No estoy en un canal de voz.")

bot.run(DISCORD_TOKEN)