import os
import asyncio
import requests
from highrise import BaseBot, Position
from flask import Flask
from threading import Thread

# Mini servidor web obligatorio para que Render mantenga el bot encendido
app = Flask('')

@app.route('/')
def home():
    return "DJBot está activo"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

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
            if not busqueda:
                await self.highrise.chat("⚠️ Por favor escribe el nombre de una canción o artista después de !play")
                return

            await self.highrise.chat(f"🎶 Buscando: {busqueda}")
            
            try:
                loop = asyncio.get_running_loop()
                response = await loop.run_in_executor(
                    None, 
                    lambda: requests.post("http://18.222.194.165:5000/play", json={"query": busqueda}, timeout=30)
                )
                
                if response.status_code == 200:
                    data = response.json()
                    titulo = data.get("title", "Audio")
                    url_streaming = data.get("url")
                    
                    if url_streaming:
                        await self.highrise.chat(f"▶️ Reproduciendo: {titulo}")
                    else:
                        await self.highrise.chat("❌ El servidor no devolvió una URL válida.")
                else:
                    await self.highrise.chat("❌ No se pudo procesar la canción en el servidor.")
                    
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

# Arrancamos el servidor web en segundo plano para Render
if __name__ == "__main__":
    t = Thread(target=run_web)
    t.daemon = True
    t.start()
