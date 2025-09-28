import os
from dotenv import load_dotenv

# Cargar variables de entorno desde un archivo .env
load_dotenv()

# Obtener el token de Discord
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

if not DISCORD_TOKEN:
    raise SystemExit(
        "ERROR: No se encontró la variable de entorno DISCORD_TOKEN. "
        "Asegúrate de tener un archivo .env en el directorio raíz con DISCORD_TOKEN=tu_token_aquí"
    )
