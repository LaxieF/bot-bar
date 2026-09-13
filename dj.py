import os
import asyncio
import requests
from highrise import BaseBot, Position

class DJBot(BaseBot):
    def __init__(self):
        super().__init__()
        self.bot_id = None

    async def on_start(self, session_metadata) -> None:
        self.bot_id = session_metadata.user_id
        print("🎧 DJBot conectado y listo para la música.", flush=True)

    async def on_chat(self, user, message: str) -> None:
        msg = message.strip()
        msg_lower = msg.lower()

        if msg_lower.startswith("!play "):
            busqueda = msg[6:].strip()
            await self.highrise.chat(f"🎶 Buscando: {busqueda}")
            
            try:
                # Ejecutamos la petición en un hilo secundario para no congelar el bot
                loop = asyncio.get_running_loop()
                response = await loop.run_in_executor(
                    None, 
                    lambda: requests.post("http://18.222.194.165:5000/play", json={"query": busqueda}, timeout=10)
                )
                
                if response.status_code == 200:
                    data = response.json()
                    titulo = data.get("title", "Audio")
                    url_streaming = data.get("url")
                    
                    await self.highrise.chat(f"▶️ Reproduciendo: {titulo}")
                    print(f"URL de streaming obtenida: {url_streaming}", flush=True)
                    # AQUÍ iría el código de reproducción de audio de tu bot hacia Highrise (si aplica)
                else:
                    await self.highrise.chat("❌ No se pudo procesar la canción.")
                    
            except Exception as e:
                print(f"Error conectando a VPS: {e}", flush=True)
                await self.highrise.chat("⚠️ Error de conexión con el servidor de música.")

        elif msg_lower == "!tpdj":
            try:
                room_users = (await self.highrise.get_room_users()).content
                for u, pos in room_users:
                    if u.username.lower() == user.username.lower():
                        x = getattr(pos, "x", 0)
                        y = getattr(pos, "y", 0)
                        z = getattr(pos, "z", 0)
                        facing = getattr(pos, "facing", "FrontRight")
                        await self.highrise.teleport(self.bot_id, Position(x, y, z, facing))
                        return
            except Exception as e:
                print(f"Error TP DJBot: {e}", flush=True)
