# filepath: c:\Users\USUARIO\Documents\Yo\Say-Lent-DJ\bot.py
import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Configurar intents del bot
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

# Crear instancia del bot
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Bot conectado como {bot.user}')
    print('Cargando cogs...')

async def load_cogs():
    """Carga todos los cogs de la carpeta 'cogs'."""
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
                print(f'  -> Cog cargado: {filename}')
            except Exception as e:
                print(f'❌ Error al cargar {filename}: {e}')

async def main():
    await load_cogs()
    await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())