from highrise import BaseBot, Position, User, CurrencyItem
import asyncio

ALL_EMOTES = [
    "dance-tiktok8", "dance-singalong", "dance-russian", "dance-poptart", "dance-pennywise",
    "dance-macarena", "dance-weird", "emote-superpose", "emote-frog", "dance-shoppingcart",
    "dance-tiktok2", "dance-duckwalk", "emote-lust", "dance-wrong", "dance-anime",
    "emote-pose1", "dance-icecream", "dance-zombieland", "dance-floss", "emote-sleigh",
    "dance-touch", "dance-aerobics", "dance-smoothwalk", "dance-hyped", "dance-jinglebell",
    "emote-celebration", "dance-kpop", "dance-handsup", "dance-breakdance", "dance-vogue",
    "idle-sleep", "emote-yes", "emote-no", "emote-shy", "emote-sad", "emote-hello",
    "emote-wave", "emote-laughing", "dance-pinguin", "emote-kiss", "emote-laughing2",
    "emote-flex", "dance-voguehands", "dance-orangejustice", "dance-sexy", "dance-disko",
    "dance-group1", "dance-group2", "dance-group3", "dance-group4", "dance-group5",
    "dance-group6", "dance-group7", "dance-group8", "dance-group9", "dance-blackpink",
    "dance-lazy", "emote-pose3", "emote-pose5", "emote-pose7", "emote-pose8",
    "dance-casual", "dance-propose", "emote-cutey", "dance-tiktok10", "emote-charging",
    "emote-confused", "emote-curtsy", "emote-fall", "dance-giggle", "emote-greedy",
    "dance-tiktok9", "emote-hot", "dance-zombie", "dance-energetic", "emote-hero",
    "dance-ghost", "dance-monster", "emote-ghostfloat", "dance-spooky", "dance-creepypose",
    "emote-headbang", "dance-rockout", "dance-heavy-metal", "dance-punk", "dance-shuffle",
    "dance-techno", "dance-samba", "dance-salsa", "dance-flamenco", "dance-bellydance",
    "emote-bow", "emote-think", "emote-peace", "emote-boxer", "dance-model", "dance-smooth"
]

# Conversión de oro a ítems de la API de Highrise
TIP_BARS = {
    1: "gold_bar_1",
    5: "gold_bar_5",
    10: "gold_bar_10",
    50: "gold_bar_50",
    100: "gold_bar_100",
    500: "gold_bar_500"
}

class AXIBot(BaseBot):
    def __init__(self):
        super().__init__()
        self.bot_id = None
        
        # DUEÑO ÚNICO
        self.owner = "LaxieF"
        self.admins = []
        self.vips = []
        
        # CONFIGURACIÓN Y UBICACIONES
        self.welcome_message = "Bienvenido/a a Drunk Bar 🍺 Escribe !ayuda o !help."
        self.locations = {}
        self.vip_zone_pos = None
        self.vip_radius = 3.0
        self.spawn_pos = None
        
        # BUCLES, FLASH Y AUTOTIP
        self.flash_users = set()
        self.user_positions = {}
        self.active_loops = {}
        self.autotip_active = False
        self.autotip_task = None

    async def on_start(self, session_metadata) -> None:
        self.bot_id = session_metadata.user_id
        print(f"🚀 AXIBot conectado. Único dueño registrado: {self.owner}")

    async def on_user_join(self, user: User, position: Position) -> None:
        if not self.spawn_pos and hasattr(position, 'x'):
            self.spawn_pos = position
        await self.highrise.chat(f"@{user.username} {self.welcome_message}")

    async def on_tip(self, sender: User, receiver: User, tip: CurrencyItem) -> None:
        if receiver.id == self.bot_id:
            await self.highrise.chat(f"🎉 ¡Gracias @{sender.username} por la propina de {tip.amount} de oro! 🪙")

    async def on_user_move(self, user: User, pos: Position) -> None:
        username_lower = user.username.lower()

        # FLASH VERTICAL
        if user.id in self.flash_users:
            old_pos = self.user_positions.get(user.id)
            if old_pos and hasattr(pos, 'y') and hasattr(old_pos, 'y'):
                if abs(pos.y - old_pos.y) >= 1.5:
                    await self.highrise.teleport(user.id, Position(pos.x, pos.y, pos.z, getattr(pos, 'facing', 'FrontRight')))
            self.user_positions[user.id] = pos

        # SEGURIDAD ZONA VIP
        if self.vip_zone_pos and username_lower != self.owner.lower() and username_lower not in [a.lower() for a in self.admins] and username_lower not in [v.lower() for v in self.vips]:
            dx, dy, dz = pos.x - self.vip_zone_pos.x, pos.y - self.vip_zone_pos.y, pos.z - self.vip_zone_pos.z
            if (dx*dx + dy*dy + dz*dz) <= (self.vip_radius * self.vip_radius):
                target_dest = self.spawn_pos if self.spawn_pos else Position(0, 0, 0)
                await self.highrise.teleport(user.id, target_dest)
                await self.highrise.send_whisper(user.id, "⛔ Zona VIP restringida.")

    async def on_chat(self, user: User, message: str) -> None:
        msg = message.strip().lower()
        args = msg.split()
        username_lower = user.username.lower()

        is_owner = username_lower == self.owner.lower()
        is_admin = is_owner or username_lower in [a.lower() for a in self.admins]

        # -------------------------------------------------------------
        # 1. AYUDA PRIVADA EN ESPAÑOL E INGLÉS
        # -------------------------------------------------------------
        if msg in ["!ayuda", "!help"]:
            if msg == "!ayuda":
                text = "✨ **MENÚ PRINCIPAL** ✨\n• !bailes [pág]\n• !stop\n• !vip\n• !ayuda admin"
            else:
                text = "✨ **MAIN MENU** ✨\n• !emotes [page]\n• !stop\n• !vip\n• !help admin"
            await self.highrise.send_whisper(user.id, text)
            return

        if msg in ["!ayuda admin", "!help admin"]:
            if is_admin:
                admin_menu = (
                    "🛡️ **ADMIN PANEL**\n"
                    "• !admin @user (Añadir/quitar Admin)\n"
                    "• !vip @user (Añadir/quitar VIP)\n"
                    "• !admins | !vips\n"
                    "• !set [zona] (Guardar punto)\n"
                    "• !come / !ven (Bot camina hacia ti)\n"
                    "• !tp @user (Teletransportar usuario)\n"
                    "• !flash (TP vertical por click)\n"
                    "• !tip @user [monto]\n"
                    "• !tipall [monto]\n"
                    "• !autotip (Lluvia de oro cada 10m)\n"
                    "• !wallet (Ver oro)"
                )
                await self.highrise.send_whisper(user.id, admin_menu)
            else:
                await self.highrise.send_whisper(user.id, "❌ Sin permisos.")
            return

        # -------------------------------------------------------------
        # 2. EMOTES Y STOP
        # -------------------------------------------------------------
        if msg.startswith("!bailes") or msg.startswith("!emotes"):
            page = int(args[1]) if len(args) > 1 and args[1].isdigit() else 1
            per_page = 15
            total_pages = (len(ALL_EMOTES) + per_page - 1) // per_page
            page = max(1, min(page, total_pages))

            start, end = (page - 1) * per_page, page * per_page
            emotes_page = ALL_EMOTES[start:end]

            formatted = [f"{start + i + 1}. !{e}" for i, e in enumerate(emotes_page)]
            await self.highrise.send_whisper(user.id, f"💃 **EMOTES (Pág {page}/{total_pages}):**\n" + ", ".join(formatted))
            return

        if msg in ["!stop", "!stopdance"]:
            if user.id in self.active_loops:
                self.active_loops[user.id].cancel()
                del self.active_loops[user.id]
            await self.highrise.send_emote("idle-sleep", user.id)
            await self.highrise.send_whisper(user.id, "🛑 Baile detenido.")
            return

        if msg.isdigit():
            num = int(msg)
            if 1 <= num <= len(ALL_EMOTES):
                await self.start_emote_loop(user.id, ALL_EMOTES[num - 1])
                return

        if msg.startswith("!") and msg[1:] in ALL_EMOTES:
            await self.start_emote_loop(user.id, msg[1:])
            return

        # -------------------------------------------------------------
        # 3. TELETRANSPORTES DE SALA
        # -------------------------------------------------------------
        if msg.startswith("!") and msg[1:] in self.locations:
            dest = self.locations[msg[1:]]
            await self.highrise.teleport(user.id, Position(dest.x, dest.y, dest.z, dest.facing))
            return

        # -------------------------------------------------------------
        # 4. ADMINISTRACIÓN CORTA Y MOVIMIENTO
        # -------------------------------------------------------------
        if is_admin:
            # Alternar Admin recortado
            if msg.startswith("!admin ") and len(args) > 1:
                target = args[1].replace("@", "")
                if target in self.admins:
                    self.admins.remove(target)
                    await self.highrise.chat(f"❌ @{target} ya no es Admin.")
                else:
                    self.admins.append(target)
                    await self.highrise.chat(f"🛡️ @{target} ahora es Admin.")

            # Alternar VIP recortado
            elif msg.startswith("!vip ") and len(args) > 1 and args[1] != "admin":
                target = args[1].replace("@", "")
                if target in self.vips:
                    self.vips.remove(target)
                    await self.highrise.chat(f"❌ @{target} ya no es VIP.")
                else:
                    self.vips.append(target)
                    await self.highrise.chat(f"💎 @{target} ahora es VIP.")

            elif msg == "!admins":
                await self.highrise.send_whisper(user.id, f"📋 Admins: {', '.join(self.admins) if self.admins else 'Ninguno'}")

            elif msg == "!vips":
                await self.highrise.send_whisper(user.id, f"📋 VIPs: {', '.join(self.vips) if self.vips else 'Ninguno'}")

            # Bot camina hacia el usuario usando la API Oficial
            elif msg in ["!come", "!ven"]:
                try:
                    room_users = (await self.highrise.get_room_users()).content
                    for u, pos in room_users:
                        if u.id == user.id:
                            await self.highrise.walk_to(Position(pos.x, pos.y, pos.z, pos.facing))
                except Exception as e:
                    print(f"Error movimiento: {e}")

            # Guardar Punto
            elif msg.startswith("!set ") and len(args) > 1:
                zone = args[1].lower()
                room_users = (await self.highrise.get_room_users()).content
                for u, pos in room_users:
                    if u.id == user.id:
                        self.locations[zone] = pos
                        if zone == "vip": self.vip_zone_pos = pos
                        await self.highrise.chat(f"📍 Punto '{zone}' guardado.")

            # Flash Vertical
            elif msg == "!flash":
                if user.id in self.flash_users:
                    self.flash_users.remove(user.id)
                    await self.highrise.send_whisper(user.id, "⚡ Flash OFF.")
                else:
                    self.flash_users.add(user.id)
                    await self.highrise.send_whisper(user.id, "⚡ Flash ON.")

            # SISTEMA DE PROPINAS Y AUTOTIP
            elif msg.startswith("!tip ") and len(args) > 2:
                target_name = args[1].replace("@", "")
                amount = int(args[2]) if args[2].isdigit() else 1
                bar_type = TIP_BARS.get(amount, "gold_bar_1")
                
                room_users = (await self.highrise.get_room_users()).content
                for u, _ in room_users:
                    if u.username.lower() == target_name.lower():
                        await self.highrise.tip_user(u.id, bar_type)
                        await self.highrise.chat(f"🪙 Tip de {amount} oro enviado a @{u.username}")

            elif msg.startswith("!tipall ") and len(args) > 1:
                amount = int(args[1]) if args[1].isdigit() else 1
                bar_type = TIP_BARS.get(amount, "gold_bar_1")
                room_users = (await self.highrise.get_room_users()).content
                for u, _ in room_users:
                    if u.id != self.bot_id:
                        await self.highrise.tip_user(u.id, bar_type)
                await self.highrise.chat(f"🎁 Lluvia de propinas de {amount} oro para todos.")

            elif msg == "!autotip" and is_owner:
                if self.autotip_active:
                    self.autotip_active = False
                    if self.autotip_task: self.autotip_task.cancel()
                    await self.highrise.chat("🛑 Auto-Tip desactivado.")
                else:
                    self.autotip_active = True
                    self.autotip_task = asyncio.create_task(self.run_autotip())
                    await self.highrise.chat("⏰ Auto-Tip activado (Cada 10 minutos).")

            elif msg in ["!wallet", "!balance"] and is_owner:
                try:
                    wallet = await self.highrise.get_wallet()
                    gold = sum([item.amount for item in wallet.content if item.type == 'gold'])
                    await self.highrise.send_whisper(user.id, f"🪙 Fondos del bot: {gold} de oro.")
                except Exception as e:
                    print(f"Error wallet: {e}")

    async def run_autotip(self):
        try:
            while self.autotip_active:
                await asyncio.sleep(600) # 10 minutos
                room_users = (await self.highrise.get_room_users()).content
                for u, _ in room_users:
                    if u.id != self.bot_id:
                        await self.highrise.tip_user(u.id, "gold_bar_1")
                await self.highrise.chat("🎁 Lluvia automática de 1 de oro entregada.")
        except asyncio.CancelledError:
            pass

    async def start_emote_loop(self, user_id: str, emote_id: str):
        if user_id in self.active_loops:
            self.active_loops[user_id].cancel()
        task = asyncio.create_task(self.run_loop(user_id, emote_id))
        self.active_loops[user_id] = task

    async def run_loop(self, user_id: str, emote_id: str):
        try:
            while True:
                await self.highrise.send_emote(emote_id, user_id)
                await asyncio.sleep(9)
        except asyncio.CancelledError:
            pass
