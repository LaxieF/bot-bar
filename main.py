from highrise import BaseBot, Position, User, CurrencyItem
import asyncio

# --- REPOSITORIO EXTENDIDO DE +100 EMOTES OFICIALES DE HIGHRISE ---
ALL_EMOTES = [
    # 1 - 20
    "dance-tiktok8", "dance-singalong", "dance-russian", "dance-poptart", "dance-pennywise",
    "dance-macarena", "dance-weird", "emote-superpose", "emote-frog", "dance-shoppingcart",
    "dance-tiktok2", "dance-duckwalk", "emote-lust", "dance-wrong", "dance-anime",
    "emote-pose1", "dance-icecream", "dance-zombieland", "dance-floss", "emote-sleigh",
    # 21 - 40
    "dance-touch", "dance-aerobics", "dance-smoothwalk", "dance-hyped", "dance-jinglebell",
    "emote-celebration", "dance-kpop", "dance-handsup", "dance-breakdance", "dance-vogue",
    "idle-sleep", "emote-yes", "emote-no", "emote-shy", "emote-sad", "emote-hello",
    "emote-wave", "emote-laughing", "dance-pinguin", "emote-kiss",
    # 41 - 60
    "emote-laughing2", "emote-flex", "dance-voguehands", "dance-orangejustice", "dance-sexy",
    "dance-disko", "dance-group1", "dance-group2", "dance-group3", "dance-group4",
    "dance-group5", "dance-group6", "dance-group7", "dance-group8", "dance-group9",
    "dance-blackpink", "dance-lazy", "emote-pose3", "emote-pose5", "emote-pose7",
    # 61 - 80
    "emote-pose8", "dance-casual", "dance-propose", "emote-cutey", "dance-tiktok10",
    "emote-charging", "emote-confused", "emote-curtsy", "emote-fall", "dance-giggle",
    "emote-greedy", "dance-tiktok9", "emote-hot", "dance-zombie", "dance-energetic",
    "emote-hero", "dance-ghost", "dance-monster", "emote-ghostfloat", "dance-spooky",
    # 81 - 100
    "dance-creepypose", "emote-headbang", "dance-rockout", "dance-heavy-metal", "dance-punk",
    "dance-shuffle", "dance-techno", "dance-samba", "dance-salsa", "dance-flamenco",
    "dance-bellydance", "emote-bow", "emote-think", "emote-peace", "emote-boxer",
    "dance-model", "dance-smooth", "emote-cute", "dance-bunny", "emote-snake",
    # 101 - 115+
    "dance-weapon", "emote-Rest", "emote-hug", "emote-cold", "dance-spiritual",
    "dance-smoothcriminal", "dance-robotic", "emote-crying", "emote-terrified", "emote-exasperated",
    "dance-groove", "dance-jingle", "dance-festive", "dance-cheerleader", "emote-tada"
]

class AXIBot(BaseBot):
    def __init__(self):
        super().__init__()
        self.bot_id = None
        
        # --- ROLES ---
        self.owners = ["LaxieF"]
        self.admins = []
        self.vips = []
        
        # --- MENSAJES Y UBICACIONES ---
        self.welcome_message = "Bienvenido/a a Drunk Bar 🍺 Escribe !ayuda para ver los comandos."
        self.locations = {}
        self.vip_zone_pos = None
        self.vip_radius = 3.0
        self.spawn_pos = None
        
        # --- BUCLES Y FLASH ---
        self.flash_users = set()
        self.user_positions = {}
        self.active_loops = {}

    async def on_start(self, session_metadata) -> None:
        self.bot_id = session_metadata.user_id
        print("🚀 AXIBot cargado con más de 100 emotes.")

    async def on_user_join(self, user: User, position: Position) -> None:
        if not self.spawn_pos and hasattr(position, 'x'):
            self.spawn_pos = position
        await self.highrise.chat(f"@{user.username} {self.welcome_message}")

    async def on_tip(self, sender: User, receiver: User, tip: CurrencyItem) -> None:
        if receiver.id == self.bot_id:
            await self.highrise.chat(f"🎉 ¡Muchísimas gracias @{sender.username} por la propina de {tip.amount} de oro! 🪙")

    async def on_user_move(self, user: User, pos: Position) -> None:
        username_lower = user.username.lower()

        # MÓDULO FLASH VERTICAL (Solo detecta saltos/pisos por altura Y >= 1.5)
        if user.id in self.flash_users:
            old_pos = self.user_positions.get(user.id)
            if old_pos and hasattr(pos, 'y') and hasattr(old_pos, 'y'):
                if abs(pos.y - old_pos.y) >= 1.5:
                    await self.highrise.teleport(user.id, Position(pos.x, pos.y, pos.z, getattr(pos, 'facing', 'FrontRight')))
            self.user_positions[user.id] = pos

        # SEGURIDAD ZONA VIP
        if self.vip_zone_pos and username_lower not in [o.lower() for o in self.owners] and username_lower not in [a.lower() for a in self.admins] and username_lower not in [v.lower() for v in self.vips]:
            dx, dy, dz = pos.x - self.vip_zone_pos.x, pos.y - self.vip_zone_pos.y, pos.z - self.vip_zone_pos.z
            if (dx*dx + dy*dy + dz*dz) <= (self.vip_radius * self.vip_radius):
                target_dest = self.spawn_pos if self.spawn_pos else Position(0, 0, 0)
                await self.highrise.teleport(user.id, target_dest)
                await self.highrise.send_whisper(user.id, "⛔ No tienes acceso a la Zona VIP. Habla con LaxieF para adquirir tu pase.")

    async def on_chat(self, user: User, message: str) -> None:
        msg = message.strip().lower()
        args = msg.split()
        username_lower = user.username.lower()

        is_owner = username_lower in [o.lower() for o in self.owners]
        is_admin = is_owner or username_lower in [a.lower() for a in self.admins]

        # -------------------------------------------------------------
        # 1. MULTILENGUAJE: AYUDA PRIVADA
        # -------------------------------------------------------------
        if msg in ["!ayuda", "!help"]:
            if msg == "!ayuda":
                text = "✨ **MENÚ PRINCIPAL** ✨\n• !bailes [página 1-8]\n• !stop (frenar baile)\n• !vip (Info VIP)\n• !ayuda admin (Dueños/Admins)"
            else:
                text = "✨ **MAIN MENU** ✨\n• !emotes [page 1-8]\n• !stop (stop dance)\n• !vip (VIP info)\n• !help admin (Owners/Admins)"
            await self.highrise.send_whisper(user.id, text)
            return

        if msg in ["!ayuda admin", "!help admin"]:
            if is_admin:
                admin_menu = (
                    "🛡️ **COMANDOS DE ADMINISTRACIÓN:**\n"
                    "• !addadmin @user | !deladmin @user\n"
                    "• !addvip @user | !delvip @user\n"
                    "• !admins | !vips | !owners\n"
                    "• !set [zona] (Guardar punto de TP)\n"
                    "• !flash (Modo TP vertical por click)\n"
                    "• !tpbot / !ven | !botwalk [zona]\n"
                    "• !wallet / !balance (Ver oro del bot)\n"
                    "• !setwelcome [mensaje]"
                )
                await self.highrise.send_whisper(user.id, admin_menu)
            else:
                await self.highrise.send_whisper(user.id, "❌ No tienes permisos de administración.")
            return

        if msg in ["!vip", "!help vip"]:
            await self.highrise.send_whisper(user.id, "💎 **ZONA VIP:** Consigue tu pase VIP contactando al dueño LaxieF.")
            return

        # -------------------------------------------------------------
        # 2. EMOTES (+100 BAILED Y PARADA LIMPIA)
        # -------------------------------------------------------------
        if msg.startswith("!bailes") or msg.startswith("!emotes"):
            page = int(args[1]) if len(args) > 1 and args[1].isdigit() else 1
            per_page = 15
            total_pages = (len(ALL_EMOTES) + per_page - 1) // per_page
            page = max(1, min(page, total_pages))

            start, end = (page - 1) * per_page, page * per_page
            emotes_page = ALL_EMOTES[start:end]

            # Muestra los números correspondientes para facilitar la selección
            formatted_emotes = [f"{start + i + 1}. !{e}" for i, e in enumerate(emotes_page)]
            text = f"💃 **EMOTES (Pág {page}/{total_pages}):**\nEscribe el número directo (ej: 45) o ![nombre]\n" + ", ".join(formatted_emotes)
            await self.highrise.send_whisper(user.id, text)
            return

        if msg in ["!stop", "!stopdance"]:
            if user.id in self.active_loops:
                self.active_loops[user.id].cancel()
                del self.active_loops[user.id]
            await self.highrise.send_emote("idle-sleep", user.id)
            await self.highrise.send_whisper(user.id, "🛑 Baile detenido.")
            return

        # Número directo (Soporta del 1 al 115+)
        if msg.isdigit():
            num = int(msg)
            if 1 <= num <= len(ALL_EMOTES):
                await self.start_emote_loop(user.id, ALL_EMOTES[num - 1])
                return

        # Comando por nombre exacto de la API (!dance-tiktok8)
        if msg.startswith("!") and msg[1:] in ALL_EMOTES:
            await self.start_emote_loop(user.id, msg[1:])
            return

        # -------------------------------------------------------------
        # 3. TELETRANSPORTES DIRECTOS (!bar, !vip, etc.)
        # -------------------------------------------------------------
        if msg.startswith("!") and msg[1:] in self.locations:
            dest = self.locations[msg[1:]]
            await self.highrise.teleport(user.id, Position(dest.x, dest.y, dest.z, dest.facing))
            return

        # -------------------------------------------------------------
        # 4. ADMINISTRACIÓN Y CONTROL DE ROLES
        # -------------------------------------------------------------
        if is_owner:
            if msg.startswith("!addowner ") and len(args) > 1:
                target = args[1].replace("@", "")
                if target not in self.owners: self.owners.append(target)
                await self.highrise.chat(f"👑 @{target} asignado/a como Dueño/a.")

            elif msg.startswith("!delowner ") and len(args) > 1:
                target = args[1].replace("@", "")
                if target in self.owners and target.lower() != "laxief":
                    self.owners.remove(target)
                    await self.highrise.chat(f"❌ @{target} removido/a de Dueños.")

            elif msg == "!owners":
                await self.highrise.send_whisper(user.id, f"📋 **Dueños:** {', '.join(self.owners)}")

            elif msg.startswith("!setwelcome "):
                self.welcome_message = message[12:].strip()
                await self.highrise.chat("✅ Mensaje de bienvenida actualizado.")

            elif msg in ["!wallet", "!balance"]:
                try:
                    wallet = await self.highrise.get_wallet()
                    gold = sum([item.amount for item in wallet.content if item.type == 'gold'])
                    await self.highrise.send_whisper(user.id, f"🪙 Balance en billetera del bot: {gold} de oro.")
                except Exception as e:
                    print(f"Error consulta wallet: {e}")

        if is_admin:
            if msg.startswith("!addadmin ") and len(args) > 1:
                target = args[1].replace("@", "")
                if target not in self.admins: self.admins.append(target)
                await self.highrise.chat(f"🛡️ @{target} ahora es Administrador/a.")

            elif msg.startswith("!deladmin ") and len(args) > 1:
                target = args[1].replace("@", "")
                if target in self.admins: self.admins.remove(target)
                await self.highrise.chat(f"❌ @{target} removido/a de Administradores.")

            elif msg == "!admins":
                await self.highrise.send_whisper(user.id, f"📋 **Admins:** {', '.join(self.admins) if self.admins else 'Ninguno.'}")

            elif msg.startswith("!addvip ") and len(args) > 1:
                target = args[1].replace("@", "")
                if target not in self.vips: self.vips.append(target)
                await self.highrise.chat(f"💎 @{target} ahora tiene acceso VIP.")

            elif msg.startswith("!delvip ") and len(args) > 1:
                target = args[1].replace("@", "")
                if target in self.vips: self.vips.remove(target)
                await self.highrise.chat(f"❌ Acceso VIP removido a @{target}.")

            elif msg == "!vips":
                await self.highrise.send_whisper(user.id, f"📋 **VIPs:** {', '.join(self.vips) if self.vips else 'Ninguno.'}")

            elif msg == "!flash":
                if user.id in self.flash_users:
                    self.flash_users.remove(user.id)
                    await self.highrise.send_whisper(user.id, "⚡ Modo Flash desactivado.")
                else:
                    self.flash_users.add(user.id)
                    await self.highrise.send_whisper(user.id, "⚡ Modo Flash Vertical activado.")

            elif msg.startswith("!set ") and len(args) > 1:
                zone = args[1].lower()
                room_users = (await self.highrise.get_room_users()).content
                for u, pos in room_users:
                    if u.id == user.id:
                        self.locations[zone] = pos
                        if zone == "vip": self.vip_zone_pos = pos
                        await self.highrise.chat(f"📍 Zona '{zone}' registrada.")

            elif msg in ["!tpbot", "!ven"]:
                room_users = (await self.highrise.get_room_users()).content
                for u, pos in room_users:
                    if u.id == user.id:
                        await self.highrise.teleport(self.bot_id, Position(pos.x, pos.y, pos.z, pos.facing))

            elif msg.startswith("!botwalk ") and len(args) > 1:
                zone = args[1].lower()
                if zone in self.locations:
                    dest = self.locations[zone]
                    await self.highrise.teleport(self.bot_id, Position(dest.x, dest.y, dest.z, dest.facing))

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
        
