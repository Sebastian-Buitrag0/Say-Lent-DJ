# Say-Lent-DJ

Un bot de música para Discord que reproduce canciones desde YouTube.

## Instalación

1. Clona este repositorio o descarga los archivos.
2. Instala las dependencias:
   ```
   pip install -r requirements.txt
   ```

## Configuración

1. Copia el archivo `.env.example` como `.env`:
   ```
   cp .env.example .env
   ```
2. Edita el archivo `.env` y agrega tu token de Discord:
   ```
   DISCORD_TOKEN=tu_token_de_discord_aquí
   ```
   **Nota:** Nunca compartas tu token de Discord. Mantén el archivo `.env` fuera del control de versiones (ya está en `.gitignore`).

## Uso

Ejecuta el bot con:

```
python music_bot.py
```

## Comandos

- `!help` - Muestra la lista de comandos disponibles.
- `!play [nombre/URL]` - Reproduce una canción o la añade a la cola.
- `!pause` - Pausa la canción actual.
- `!resume` - Reanuda la canción pausada.
- `!skip` - Salta a la siguiente canción.
- `!stop` - Detiene la música y limpia la cola.
- `!queue` - Muestra la cola de reproducción.
- `!clear` - Limpia la cola.
- `!join` - Hace que el bot se una a tu canal de voz.
- `!leave` - Desconecta el bot del canal de voz.

## Estructura del Proyecto

- `music_bot.py` - Archivo principal del bot.
- `config.py` - Configuración y carga del token.
- `cogs/` - Directorio con los módulos del bot.
  - `music_cog.py` - Comandos de música.
  - `general_cog.py` - Comandos generales (como help).
- `requirements.txt` - Dependencias del proyecto.
- `.env` - Archivo de configuración (no incluido en el repositorio).
