import os
from highrise import BaseBot, Position, run

class DJBot(BaseBot):
    def __init__(self):
        super().__init__()
        self.bot_id = None

    async def on_start(self, session_metadata) -> None:
        self.bot_id = session_metadata.user_id
        print("🎧 DJBot conectado y listo para la música.", flush=True)

    async def on_chat(self, user, message: str) -> None:
        msg = message.strip().lower()

        if msg == "!play":
            await self.highrise.chat("🎶 ¡Poniendo la música!")
            
        elif msg == "!tpdj":
            try:
                room_users = (await self.highrise.get_room_users()).content
                for u, pos in room_users:
                    if u.username.lower() == user.username.lower():
                        x = getattr(pos, 'x', 0)
                        y = getattr(pos, 'y', 0)
                        z = getattr(pos, 'z', 0)
                        facing = getattr(pos, 'facing', 'FrontRight')
                        await self.highrise.teleport(self.bot_id, Position(x, y, z, facing))
                        return
            except Exception as e:
                print(f"Error TP DJBot: {e}", flush=True)

if __name__ == "__main__":
    ROOM_ID = "66137b812eb7852780780ace"
    TOKEN ="d56c280270fa345592ce1ed994ae8ade013e9fa9c48ae744e03eef57278f87a0"
    
    # Inicia la conexión del DJ con Highrise
    run(DJBot(), ROOM_ID, TOKEN)
        
