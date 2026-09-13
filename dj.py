import os
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
                requests.post("http://18.222.194.165:5000/play", json={"query": busqueda}, timeout=5)
            except Exception as e:
                print(f"Error conectando a VPS: {e}", flush=True)

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
