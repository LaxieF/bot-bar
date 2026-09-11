from highrise import BaseBot, Position, User, CurrencyItem
import asyncio

# --- REPOSITORIO DE EMOTES ---
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

TIP_BARS = {
    1: "gold_bar_1", 5: "gold_bar_5", 10: "gold_bar_10",
    50: "gold_bar_50", 100: "gold_bar_100", 500: "gold_bar_500"
}

class AXIBot(BaseBot):
    def __init__(self):
        super().__init__()
        self.bot_id = None
        self.owner = "LaxieF"
        self.admins = []
        self.vips = []
        
        self.welcome_message = "Bienvenido/a a Drunk Bar 🍺 Escribe !ayuda o !help."
        self.locations = {}
        self.vip_zone_pos = None
        self.vip_radius = 3.0
        self.spawn_pos = None
        self.default_bot_pos = None
        
        self.flash_users = set()
        self.user_positions = {}
        self.active_loops = {}
        
        self.following_user_id = None
        self.follow_task = None
        
        self.autotip_active = False
        self.autotip_task = None

    async def on_start(self, session_metadata) -> None:
        self.bot_id = session_metadata.user_id
        print(f"🎧 DJBot conectado y listo para la música.")

    async def on_user_join(self, user: User, position: Position) -> None:
        if not self.spawn_pos and hasattr(position, 'x'):
            self.spawn_pos = position
        await self.highrise.chat(f"@{user.username} {self.welcome_message}")

    async def on_tip(self, sender: User, receiver: User, tip: CurrencyItem) -> None:
        if receiver.id == self.bot_id:
            await self.highrise.chat(f"🎉 ¡Gracias @{sender.username} por la propina de {tip.amount} de oro! 🪙")

    async def on_user_move(self, user: User, pos: Position) -> None:
        username_lower = user.username.lower()

        if self.following_user_id and user.id == self.following_user_id:
            try:
                await self.highrise.walk_to(Position(pos.x, pos.y, pos.z, getattr(pos, 'facing', 'FrontRight')))
            except Exception as e:
                print(f"Error follow: {e}")

        if user.id in self.flash_users:
            old_pos = self.user_positions.get(user.id)
            if old_pos and hasattr(pos, 'y') and hasattr(old_pos, 'y'):
                if abs(pos.y - old_pos.y) >= 1.5:
                    await self.highrise.teleport(user.id, Position(pos.x, pos.y, pos.z, getattr(pos, 'facing', 'FrontRight')))
            self.user_positions[user.id] = pos

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

        # --- MENÚ PRINCIPAL EN COLORES ---
        if msg in ["!ayuda", "!help", "/help"]:
            menu = (
                "<color=#F2C94C>✨ Command Categories: ✨</color>\n"
                "<i>Type /help to see commands in that category.</i>\n\n"
                "💃 <color=#E282B7>/help emotes</color>\n"
                "🚀 <color=#7CB9E8>/help tp</color>\n"
                "🎮 <color=#A892EE>/help fun</color>\n"
                "🪙 <color=#F2C94C>/help gold</color>\n"
                "🛡️ <color=#FF7F50>/help mod</color>\n"
                "⚙️ <color=#FF4500>/help admin</color>"
            )
            await self.highrise.send_whisper(user.id, menu)
            return

        if msg in ["!ayuda emotes", "!help emotes", "/help emotes"]:
            text = "💃 <color=#E282B7>**EMOTES MENU**</color>\n• !emotes [pág 1-8]\n• Escribe el número directo (1 al 100+) para bailar en bucle.\n• Escribe !stop en el chat general para detenerte."
            await self.highrise.send_whisper(user.id, text)
            return

        if msg in ["!ayuda tp", "!help tp", "/help tp"]:
            tp_list = ", ".join([f"!{loc}" for loc in self.locations.keys()]) if self.locations else "Ninguna aún"
            text = f"🚀 <color=#7CB9E8>**TELEPORTS**</color>\n• Lugares: {tp_list}\n\n⚡ **MODO FLASH:** Dar click en un nivel superior te teletransportará verticalmente."
            await self.highrise.send_whisper(user.id, text)
            return

        if msg in ["!ayuda fun", "!help fun", "/help fun"]:
            text = "🎮 <color=#A892EE>**FUN COMMANDS**</color>\n• !heart @user\n• !hug @user\n• !wink @user\n• !clap @user"
            await self.highrise.send_whisper(user.id, text)
            return

        if msg in ["!ayuda gold", "!help gold", "/help gold"]:
            text = "🪙 <color=#F2C94C>**GOLD & TIPS**</color>\n• !tip @user [monto]\n• !tipall [monto]\n• !wallet"
            await self.highrise.send_whisper(user.id, text)
            return

        if msg in ["!ayuda mod", "!help mod", "/help mod"]:
            if is_admin:
                text = "🛡️ <color=#FF7F50>**MODERATION**</color>\n• !kick @user\n• !ban @user | !unban @user\n• !mute @user | !unmute @user"
                await self.highrise.send_whisper(user.id, text)
            else:
                await self.highrise.send_whisper(user.id, "❌ No tienes permisos de moderación.")
            return

        if msg in ["!ayuda admin", "!help admin", "/help admin"]:
            if is_admin:
                text = (
                    "⚙️ <color=#FF4500>**ADMIN PANEL**</color>\n"
                    "• !follow @user | !unfollow\n"
                    "• !tpbot\n"
                    "• !setbot\n"
                    "• !set [zona]\n"
                    "• !admin @user | !vip @user\n"
                    "• !admins | !vips\n"
                    "• !flash\n"
                    "• !autotip"
                )
                await self.highrise.send_whisper(user.id, text)
            else:
                await self.highrise.send_whisper(user.id, "❌ Sin permisos de administración.")
            return

        # --- EMOTES & BAILED ---
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

        # --- REACCIONES ---
        if msg.startswith("!heart ") and len(args) > 1:
            await self.highrise.send_emote("emote-lust", user.id)
            await self.highrise.chat(f"❤️ @{user.username} le manda un corazón a {args[1]}")

        elif msg.startswith("!hug ") and len(args) > 1:
            await self.highrise.send_emote("emote-hug", user.id)
            await self.highrise.chat(f"🤗 @{user.username} le da un abrazo a {args[1]}")

        elif msg.startswith("!wink ") and len(args) > 1:
            await self.highrise.send_emote("emote-pose1", user.id)
            await self.highrise.chat(f"😉 @{user.username} le guiña el ojo a {args[1]}")

        elif msg.startswith("!clap ") and len(args) > 1:
            await self.highrise.send_emote("emote-celebration", user.id)
            await self.highrise.chat(f"👏 @{user.username} le aplaude a {args[1]}")

        # --- TELEPORTS ---
        if msg.startswith("!") and msg[1:] in self.locations:
            dest = self.locations[msg[1:]]
            await self.highrise.teleport(user.id, Position(dest.x, dest.y, dest.z, getattr(dest, 'facing', 'FrontRight')))
            return

        # --- ADMIN / MOD COMMANDS ---
        if is_admin:
            if msg.startswith("!follow ") and len(args) > 1:
                target_name = args[1].replace("@", "").lower()
                room_users = (await self.highrise.get_room_users()).content
                found = False
                for u, _ in room_users:
                    if u.username.lower() == target_name:
                        self.following_user_id = u.id
                        found = True
                        await self.highrise.chat(f"🚶 El bot ahora está siguiendo a @{u.username}")
                        break
                if not found:
                    await self.highrise.send_whisper(user.id, "❌ Usuario no encontrado.")

            elif msg == "!unfollow":
                self.following_user_id = None
                await self.highrise.chat("🛑 El bot dejó de seguir.")

            elif msg == "!tpbot":
                room_users = (await self.highrise.get_room_users()).content
                for u, pos in room_users:
                    if u.id == user.id:
                        await self.highrise.teleport(self.bot_id, Position(pos.x, pos.y, pos.z, getattr(pos, 'facing', 'FrontRight')))

            elif msg == "!setbot":
                room_users = (await self.highrise.get_room_users()).content
                for u, pos in room_users:
                    if u.id == user.id:
                        self.default_bot_pos = pos
                        await self.highrise.chat("📍 Posición por defecto del bot guardada.")

            elif msg.startswith("!set ") and len(args) > 1:
                zone = args[1].lower()
                room_users = (await self.highrise.get_room_users()).content
                for u, pos in room_users:
                    if u.id == user.id:
                        self.locations[zone] = pos
                        if zone == "vip": self.vip_zone_pos = pos
                        await self.highrise.chat(f"📍 Punto '{zone}' guardado.")

            elif msg.startswith("!admin ") and len(args) > 1:
                target = args[1].replace("@", "")
                if target in self.admins:
                    self.admins.remove(target)
                    await self.highrise.chat(f"❌ @{target} ya no es Admin.")
                else:
                    self.admins.append(target)
                    await self.highrise.chat(f"🛡️ @{target} ahora es Admin.")

            elif msg.startswith("!vip ") and len(args) > 1 and args[1] not in ["admin", "tp"]:
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

            elif msg == "!flash":
                if user.id in self.flash_users:
                    self.flash_users.remove(user.id)
                    await self.highrise.send_whisper(user.id, "⚡ Flash OFF.")
                else:
                    self.flash_users.add(user.id)
                    await self.highrise.send_whisper(user.id, "⚡ Flash ON.")

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
                await self.highrise.chat(f"🎁 Lluvia de propinas de {amount} oro para la sala.")

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
                await asyncio.sleep(600)
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
