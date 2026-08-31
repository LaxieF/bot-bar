from bot.radio import descargar_de_youtube
import json
import os
import re
import subprocess
from highrise import BaseBot, Position, CurrencyItem, Item, User

CONFIG_FILE = "dj_config.json"

def clean_song_title(title: str) -> str:
    """Limpia etiquetas molestas de los títulos de YouTube"""
    patterns = [
        r'\((official|video|music|audio|lyric|hd|4k).*?\)',
        r'\[(official|video|music|audio|lyric|hd|4k).*?\]',
        r'\(video oficial.*?\)',
        r'\[video oficial.*?\]',
        r'\(audio oficial.*?\)',
        r'\[audio oficial.*?\]'
    ]
    cleaned = title
    for pattern in patterns:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
    # Quitar espacios dobles sobrantes
    return " ".join(cleaned.split())

class DJBot(BaseBot):
    def __init__(self):
        super().__init__()
        # Diccionario para recordar qué usuarios han pagado oro y tienen derecho a una canción
        self.usuarios_pagados = {} 
        # Variable para guardar tu URL base de Replit de forma dinámica
        # REEMPLAZA ESTO CON TU LINK REAL DE REPLIT (.replit.dev)
                # El bot detectará su propio link de internet automáticamente de forma invisible
        self.url_base_replit = f"https://{os.environ.get('REPL_SLUG')}.{os.environ.get('REPL_OWNER')}.replit.dev".lower()


    async def on_start(self, session_metadata) -> None:
        """Se ejecuta cuando el bot entra con éxito a la sala pública"""
        print(f"[DJ Bot] Bot en línea. ID de la sesión: {session_metadata.session_id}")
        # Guardamos el ID del bot para usarlo en las validaciones
        self.bot_id = session_metadata.user_id

    async def on_tip(self, sender: User, receiver: User, tip: CurrencyItem) -> None:
        """Detecta cuando un usuario envía una propina/oro en la sala"""
        # Validamos que el oro sea enviado al bot
        if receiver.id == self.bot_id:
            
            # COSTO DE LA CANCIÓN: Cambia el 5 por la cantidad de oro que quieras cobrar
            if tip.amount >= 5:
                # Le damos el derecho al usuario de pedir 1 canción
                self.usuarios_pagados[sender.id] = True
                
                await self.highrise.chat(
                    f"¡Gracias por tus {tip.amount}g, @{sender.username}! "
                    f"Escribe en el chat: !pedir nombre de la canción"
                )

    async def on_chat(self, user: User, message: str) -> None:
        """Detecta los mensajes del chat para procesar el comando !pedir"""
        texto = message.strip()
        
        if texto.startswith("!pedir "):
            # Verificamos si el usuario pagó previamente su oro
            if user.id in self.usuarios_pagados and self.usuarios_pagados[user.id]:
                # Extraemos todo el texto que viene después de la palabra !pedir
                nombre_cancion = texto[7:].strip()
                
                if not nombre_cancion:
                    await self.highrise.chat(f"@{user.username}, debes escribir el nombre de una canción después de !pedir.")
                    return

                # Limpiamos el título con tu función nativa para anunciarla bonito
                nombre_limpio = clean_song_title(nombre_cancion)
                await self.highrise.chat(f"🔍 Buscando y sintonizando: '{nombre_limpio}'... Espera unos segundos.")
                
                try:
                    # El servidor de Replit descarga y convierte el video en MP3 en segundo plano
                    archivo_mp3 = descargar_de_youtube(nombre_cancion)
                    
                    # Generamos el enlace directo .mp3 que Highrise necesita
                    url_publica_audio = f"{self.url_base_replit}/stream/{archivo_mp3}"
                    
                    # Ordenamos a la sala que reproduzca el flujo de audio
                    await self.highrise.set_sound_source(url_publica_audio)
                    
                    # Quitamos el permiso de la lista porque ya consumió su canción pagada
                    self.usuarios_pagados[user.id] = False
                    
                    await self.highrise.chat(f"📻 Sonando ahora en la sala: {nombre_limpio}")
                    
                except Exception as error:
                    print(f"[Error Jukebox]: {error}")
                    await self.highrise.chat("❌ Hubo un inconveniente al cargar el audio. Por favor intenta con otra canción.")
            else:
                # Si intenta usar el comando sin haber pagado oro antes
                await self.highrise.chat(f"@{user.username}, para pedir una canción primero debes enviar una propina de 5g al bot.")
                
