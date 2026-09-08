import os
import requests
import asyncio
from highrise import BaseBot, User

# --- MOTOR DE LA API DE MÚSICA ---
def buscar_musica_api(nombre_cancion):
    """
    Busca una canción en la API externa y devuelve una URL .mp3 limpia
    para que el bot DJ la pegue de forma automática en la sala.
    """
    url_api = f"https://vevo.guru{nombre_cancion}"
    try:
        response = requests.get(url_api, timeout=10)
        if response.status_code == 200:
            datos = response.json()
            if "results" in datos and len(datos["results"]) > 0:
                # Extraemos el enlace de audio directo .mp3
                return datos["results"]["download_url"]
        return None
    except Exception as e:
        print(f"Error al conectar con la API de música: {e}")
        return None

# --- CLASE DEL BOT DJ ---
class MusicBot(BaseBot):
    def __init__(self):
        super().__init__()
        # Diccionario para recordar quién ya pagó por su canción
        self.creditos_musica = {}
        # IMPORTANTE: Reemplaza esto con el ID real de la cuenta de tu BOT DJ
        self.bot_dj_id = "ID_DE_TU_BOT_DJ_AQUI" 
        # Costo predeterminado de la canción (puedes cambiarlo si quieres)
        self.PRECIO_CANCION = 5 

    async def on_tip(self, sender_id: str, receiver_id: str, tip: tuple) -> None:
        """Se activa cuando un jugador le da propina al Bot DJ"""
        cantidad, moneda = tip
        
        # Validamos que la propina sea en Gold y dirigida a este bot específicamente
        if receiver_id == self.bot_dj_id and moneda == "gold":
            if cantidad >= self.PRECIO_CANCION:
                await self.highrise.send_whisper(sender_id, "✅ ¡Pago de música recibido! Ahora escribe en el chat: !play [nombre de la canción]")
                # Guardamos el crédito del jugador
                self.creditos_musica[sender_id] = True
            else:
                await self.highrise.send_whisper(sender_id, f"❌ La canción cuesta {self.PRECIO_CANCION} Gold. Me diste {cantidad}.")

    async def on_chat(self, user: User, message: str) -> None:
        """Escucha el comando !play en el chat público de la sala"""
        if message.startswith("!play "):
            # Verificamos si el usuario pagó previamente en el evento on_tip
            if user.id in self.creditos_musica and self.creditos_musica[user.id]:
                # Extraemos el nombre de la canción
                nombre_cancion = message.replace("!play ", "").strip()
                
                await self.highrise.send_chat_message(f"🔍 [DJ] Buscando '{nombre_cancion}' para {user.username}...")
                
                # Buscamos la URL directa .mp3
                url_mp3 = buscar_musica_api(nombre_cancion)
                
                if url_mp3:
                    try:
                        # ¡Aquí el bot cambia la casilla URL de la sala automáticamente!
                        # REQUISITO: El Bot DJ debe tener permisos de DISEÑADOR en la sala
                        await self.highrise.set_room_audio(url=url_mp3)
                        
                        await self.highrise.send_chat_message(f"🎵 [DJ] Sonando ahora: {nombre_cancion}")
                        # Consumimos su crédito
                        self.creditos_musica[user.id] = False 
                    except Exception as e:
                        print(f"Error al meter la URL en Highrise: {e}")
                        await self.highrise.send_whisper(user.id, "❌ Error del servidor de Highrise al cambiar el reproductor.")
                else:
                    await self.highrise.send_whisper(user.id, "❌ No encontré esa canción. Intenta con otro nombre o artista.")
            else:
                await self.highrise.send_whisper(user.id, "⚠️ Debes dar una propina de Gold al Bot DJ antes de pedir música.")

# Función estándar para iniciar este bot de forma independiente si fuera necesario
def iniciar_dj():
    from highrise.__main__ import main
    # Cambia 'archivo:Clase' por cómo se llame tu ejecución si usas variables de entorno
    # Por ejemplo, si usas la herramienta estándar de ejecución del SDK:
    os.environ["BOT_TOKEN"] = "TOKEN_DE_TU_BOT_DJ_AQUI"
    os.environ["ROOM_ID"] = "ID_DE_TU_SALA_AQUI"
    main()

if __name__ == "__main__":
    iniciar_dj()
            
