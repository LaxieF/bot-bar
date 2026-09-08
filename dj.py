import requests
import asyncio
from highrise import BaseBot, User

def buscar_musica_api(nombre_cancion):
    """
    Se conecta a la API de conversión externa para transformar el texto 
    del usuario en una URL directa de streaming .mp3 que Highrise sí acepte.
    """
    # Endpoint público de conversión de música
    url_api = f"https://vevo.guru{nombre_cancion}"
    
    try:
        response = requests.get(url_api, timeout=10)
        if response.status_code == 200:
            datos = response.json()
            # Validamos que la API externa haya encontrado el archivo de audio
            if "results" in datos and len(datos["results"]) > 0:
                # Extraemos el enlace .mp3 directo generado en la nube
                url_directa_mp3 = datos["results"]["download_url"]
                return url_directa_mp3
        return None
    except Exception as e:
        print(f"Error en la API externa de música: {e}")
        return None

class MusicBot(BaseBot):
    def __init__(self):
        super().__init__()
        # Diccionario para controlar los créditos de los jugadores que pagan
        self.creditos_musica = {}
        # IMPORTANTE: Pon aquí el ID exacto de la cuenta de tu Bot DJ
        self.bot_dj_id = "TU_BOT_DJ_ID_REAL" 
        # Precio de la canción en Gold
        self.precio_cancion = 5 

    async def on_tip(self, sender_id: str, receiver_id: str, tip: tuple) -> None:
        """Controla el dinero (Gold) que recibe el Bot DJ"""
        cantidad, moneda = tip
        
        # Validamos que el pago sea en Gold y directo para el Bot DJ
        if receiver_id == self.bot_dj_id and moneda == "gold":
            if cantidad >= self.precio_cancion:
                await self.highrise.send_whisper(sender_id, f"✅ ¡Pago recibido! Escribe en el chat: !play [nombre de tu canción]")
                self.creditos_musica[sender_id] = True
            else:
                await self.highrise.send_whisper(sender_id, f"❌ El costo es de {self.precio_cancion} Gold. Me diste {cantidad}.")

    async def on_chat(self, user: User, message: str) -> None:
        """Escucha el comando para activar la música en la sala"""
        if message.startswith("!play "):
            # Verificamos si el usuario ya pagó previamente su crédito
            if user.id in self.creditos_musica and self.creditos_musica[user.id]:
                nombre_cancion = message.replace("!play ", "").strip()
                
                await self.highrise.send_chat_message(f"🔍 [DJ] Buscando '{nombre_cancion}'...")
                
                # Obtenemos la URL directa desde la API externa
                url_mp3_sala = buscar_musica_api(nombre_cancion)
                
                if url_mp3_sala:
                    try:
                        # EN ESTA LÍNEA EL BOT PEGA EL ENLACE EN LA CASILLA DE LA SALA AUTOMÁTICAMENTE
                        # Recordatorio: Tu Bot DJ necesita permisos de DISEÑADOR en la sala de Highrise
                        await self.highrise.set_room_audio(url=url_mp3_sala)
                        
                        await self.highrise.send_chat_message(f"🎵 [DJ] Sonando ahora: {nombre_cancion}")
                        self.creditos_musica[user.id] = False # Consumimos el crédito cobrado
                    except Exception as e:
                        print(f"Error al meter la URL en Highrise: {e}")
                        await self.highrise.send_whisper(user.id, "❌ El juego rechazó la URL. Verifica mis permisos de Diseñador.")
                else:
                    await self.highrise.send_whisper(user.id, "❌ No se pudo extraer el audio de esa canción. Intenta con otra.")
            else:
                await self.highrise.send_whisper(user.id, "⚠️ Debes darle una propina de Gold al Bot DJ primero.")
        
