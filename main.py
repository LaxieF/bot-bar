from highrise import BaseBot, Position

class AXIBot(BaseBot):
    def __init__(self):
        super().__init__()
        self.bot_id = None

    async def on_start(self, session_metadata) -> None:
        self.bot_id = session_metadata.user_id
        print("🚀 AXIBot (Moderación) conectado y listo.")

    async def on_user_join(self, user, position) -> None:
        await self.highrise.chat(f"AXIBot Bienvenido a Drunk Bar 🍺")

    async def on_chat(self, user, message: str) -> None:
        msg = message.strip().lower()

        if msg == "!help":
            await self.highrise.send_whisper(user.id, "👑 **HERRAMIENTAS VIP / MOD:**\n• !kick @usuario\n• !mute @usuario [minutos]\n• !unmute @usuario")
            await self.highrise.send_whisper(user.id, "🛠️ **HERRAMIENTAS DE DUEÑO:**\n• !settp - Guardar zona actual.\n• !msg - Cambiar mensaje automático.\n• !timer - Cambiar tiempo de anuncio.\n• !addvip @usuario | !removevip @usuario\n• !ban @usuario")

        elif msg == "!tpbot":
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
                print(f"Error TP AXIBot: {e}")
              
