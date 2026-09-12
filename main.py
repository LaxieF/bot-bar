from highrise import BaseBot, Position, User, CurrencyItem
import asyncio
import sys
import os
import time

# MAPA DE REACCIONES FLOTANTES OFICIALES DE HIGHRISE (en minúsculas)
REACTIONS = {
    "heart": "heart",
    "wink": "wink",
    "wave": "wave",
    "clap": "clap",
    "thumbs": "thumbs"
}

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

class AXIBot(BaseBot):
    def __init__(self):
        super().__init__()
        self.bot_id = None
        self.owner = "LaxieF"
        self.admins = []
        
        # Guardado en Memoria (Evita crash de escritura en disco Render)
        self.vips = []
        self.bot_fixed_pos = None
        self.locations = {}
        
        # Mutes y rastreo de posición vertical
        self.muted_users = {}
        self.user_last_y = {}
        
        # Estado de Flash TP
        self.flash_enabled = False
        
        # Estado de Follow
        self.following_target = None
        self.follow_task = None

        # MENSAJES PERSONALIZABLES
        self.welcome_message = "Bienvenido/a a Drunk Bar 🍺 Escribe !ayuda o !help."
        self.promo_message = "🌟 ¡Consigue acceso VIP permanente enviando una propina de 500g al bot!"
        self.promo_interval = 300  # 5 minutos
        self.promo_active = True
        self.promo_task = None
        
        self.vip_zone_pos = None
        self.vip_radius = 3.0
        self.spawn_pos = None
        
        self.active_loops = {}
        self.user_cooldowns = {}
        self.cooldown_time = 2.0

    async def on_start(self, session_metadata) -> None:
        self.bot_id = session_metadata.user_id
        print(f"🎧 DJBot conectado y listo.")
        
        if self.bot_fixed_pos:
            try:
                pos = Position(self.bot_fixed_pos['x'], self.bot_fixed_pos['y'], self.bot_fixed_pos['z'])
                await self.highrise.teleport(self.bot_id, pos)
            except Exception as e:
                print(f"Error reposicionando bot: {e}")

        if self.promo_active:
            self.promo_task = asyncio.create_task(self.run_promo_loop())

    async def on_user_join(self, user: User, position: Position) -> None:
        if not self.spawn_pos and hasattr(position, 'x'):
            self.spawn_pos = position
        try:
            await self.highrise.chat(f"@{user.username} {self.welcome_message}")
        except Exception as e:
            print(f"Error bienvenida: {e}")

    async def on_tip(self, sender: User, receiver: User, tip: CurrencyItem) -> None:
        if receiver.id == self.bot_id:
            print(f"💰 [PROPINA] @{sender.username} envió {tip.amount}g de oro.")
            await self.highrise.chat(f"🎉 ¡Gracias @{sender.username} por la propina de {tip.amount}g de oro! 🪙")
            
            if tip.amount >= 500:
                if sender.username not in self.vips:
                    self.vips.append(sender.username)
                    await self.highrise.chat(f"💎 ¡Felicidades @{sender.username}! Ahora eres miembro VIP.")

    async def on_user_move(self, user: User, pos: Position) -> None:
        username_lower = user.username.lower()
        is_owner = username_lower == self.owner.lower()
        is_admin = is_owner or username_lower in [a.lower() for a in self.admins]
        is_vip = is_admin or username_lower in [v.lower() for v in self.vips]

        # Restricción de Zona VIP
        if self.vip_zone_pos and not is_vip:
            vip_pos = Position(self.vip_zone_pos['x'], self.vip_zone_pos['y'], self.vip_zone_pos['z'])
            dx, dy, dz = pos.x - vip_pos.x, pos.y - vip_pos.y, pos.z - vip_pos.z
            if (dx*dx + dy*dy + dz*dz) <= (self.vip_radius * self.vip_radius):
                target_dest = self.spawn_pos if self.spawn_pos else Position(0, 0, 0)
                await self.highrise.teleport(user.id, target_dest)
                await self.highrise.send_whisper(user.id, "⛔ Zona VIP restringida. Compra VIP enviando 500g al bot.")
                return

        # Flash TP sólo en cambios verticales (eje Y)
        if self.flash_enabled:
            last_y = self.user_last_y.get(user.id, pos.y)
            if abs(pos.y - last_y) > 1.5:
                if self.vip_zone_pos and not is_vip:
                    vip_pos = Position(self.vip_zone_pos['x'], self.vip_zone_pos['y'], self.vip_zone_pos['z'])
                    if abs(pos.y - vip_pos.y) < 2.0:
                        await self.highrise.send_whisper(user.id, "⛔ No tienes acceso VIP para este piso.")
                        return
                await self.highrise.teleport(user.id, pos)
            self.user_last_y[user.id] = pos.y

    async def run_promo_loop(self):
        try:
            while self.promo_active:
                await asyncio.sleep(self.promo_interval)
                if self.promo_message:
                    await self.highrise.chat(self.promo_message)
        except asyncio.CancelledError:
            pass

    async def run_follow_loop(self):
        try:
            while self.following_target:
                room_users = (await self.highrise.get_room_users()).content
                for u, pos in room_users:
                    if u.id == self.following_target:
                        await self.highrise.walk_to(Position(pos.x + 1, pos.y, pos.z))
                        break
                await asyncio.sleep(2)
        except asyncio.CancelledError:
            pass

    async def on_chat(self, user: User, message: str) -> None:
        msg = message.strip().lower()
        args = message.strip().split()
        username_lower = user.username.lower()

        is_owner = username_lower == self.owner.lower()
        is_admin = is_owner or username_lower in [a.lower() for a in self.admins]

        # Comprobación de Mute
        if user.id in self.muted_users:
            if time.time() < self.muted_users[user.id]:
                return
            else:
                del self.muted_users[user.id]

        # Anti-Spam
        current_time = time.time()
        if not is_admin:
            if user.id in self.user_cooldowns:
                if current_time - self.user_cooldowns[user.id] < self.cooldown_time:
                    return
            self.user_cooldowns[user.id] = current_time

        # --- REINICIO DEL BOT (Solo Owner) ---
        if msg in ["!restart", "!reiniciar"] and is_owner:
            await self.highrise.chat("🔄 Reiniciando el bot...")
            os.execv(sys.executable, ['python'] + sys.argv)

        # --- GESTIÓN DE SEGUIMIENTO (FOLLOW / UNFOLLOW) ---
        if msg in ["!follow", "!sigueme"] and is_admin:
            self.following_target = user.id
            if self.follow_task: self.follow_task.cancel()
            self.follow_task = asyncio.create_task(self.run_follow_loop())
            await self.highrise.chat(f"🏃 Siguiendo a @{user.username}")
            return

        if msg.startswith("!follow ") and is_admin and len(args) > 1:
            target_search = args[1].replace("@", "").lower()
            room_users = (await self.highrise.get_room_users()).content
            for u, _ in room_users:
                if u.username.lower() == target_search:
                    self.following_target = u.id
                    if self.follow_task: self.follow_task.cancel()
                    self.follow_task = asyncio.create_task(self.run_follow_loop())
                    await self.highrise.chat(f"🏃 Siguiendo a @{u.username}")
                    break
            return

        if msg in ["!unfollow", "!stopfollow"] and is_admin:
            if self.follow_task:
                self.follow_task.cancel()
                self.follow_task = None
            self.following_target = None
            await self.highrise.chat("🛑 Bot detenido.")
            return

        # --- MENÚS DE AYUDA ---
        if msg in ["!ayuda", "!help", "/help"]:
            menu = (
                "<color=#F2C94C>✨ Categorías de Comandos: ✨</color>\n\n"
                "💃 <color=#E282B7>/help emotes</color>\n"
                "🚀 <color=#7CB9E8>/help tp</color>\n"
                "❤️ <color=#A892EE>/help react</color>\n"
                "💬 <color=#00FFFF>/help messages</color>\n"
                "🛡️ <color=#FF7F50>/help mod</color>\n"
                "⚙️ <color=#FF4500>/help admin</color>"
            )
            await self.highrise.send_whisper(user.id, menu)
            return

        if msg in ["/help emotes", "!help emotes"]:
            text = "💃 **COMANDOS DE EMOTES**\n• Escribe un número del 1 al 100 para bailar.\n• !stop - Detener el baile."
            await self.highrise.send_whisper(user.id, text)
            return

        if msg in ["/help tp", "!help tp"]:
            tp_list = ", ".join([f"!{k}" for k in self.locations.keys()]) if self.locations else "Ninguno"
            text = f"🚀 **TELETRANSPORTE**\n• Puntos TP guardados: {tp_list}\n• !summon @user (Traer usuario)\n• !goto @user (Ir a usuario)\n• !tpbot (Traer bot)\n• 🌟 Acceso VIP enviando 500g al bot."
            await self.highrise.send_whisper(user.id, text)
            return

        if msg in ["/help react", "!help react"]:
            text = "❤️ **REACCIONES FLOTANTES**\n• !heart [@user]\n• !wink [@user]\n• !wave [@user]\n• !clap [@user]\n• !thumbs [@user]"
            await self.highrise.send_whisper(user.id, text)
            return

        if msg in ["/help messages", "!help messages"] and is_admin:
            text = (
                "💬 **CONFIGURACIÓN DE MENSAJES**\n"
                "• !setwelcome <texto> / !resetwelcome\n"
                "• !setpromotext <texto> / !resetpromo\n"
                "• !setpromotime <minutos>\n"
                "• !promoon / !promooff"
            )
            await self.highrise.send_whisper(user.id, text)
            return

        if msg in ["/help mod", "!help mod"] and is_admin:
            text = "🛡️ **MODERACIÓN**\n• !kick @user\n• !mute @user <minutos>\n• !unmute @user\n• !vip @user\n• !vips"
            await self.highrise.send_whisper(user.id, text)
            return

        if msg in ["/help admin", "!help admin"] and is_admin:
            text = (
                "⚙️ **ADMINISTRACIÓN**\n"
                "• !set <nombre> - Guardar punto TP.\n"
                "• !del <nombre> - Eliminar punto TP.\n"
                "• !setbot - Guardar posición fija del bot.\n"
                "• !tpbot - Traer al bot a ti.\n"
                "• !summon @user / !goto @user\n"
                "• !flash on/off - Portales verticales.\n"
                "• !follow / !unfollow\n"
                "• !restart"
            )
            await self.highrise.send_whisper(user.id, text)
            return

        # --- REACCIONES FLOTANTES NATIVAS ---
        if msg.startswith(("!heart", "!wink", "!wave", "!clap", "!thumbs")):
            cmd = msg.split()[0][1:]
            reaction_type = REACTIONS.get(cmd)
            if reaction_type:
                target_user_id = user.id
                if len(args) > 1:
                    target_search = args[1].replace("@", "").lower()
                    room_users = (await self.highrise.get_room_users()).content
                    for u, _ in room_users:
                        if u.username.lower() == target_search:
                            target_user_id = u.id
                            break
                try:
                    await self.highrise.react(reaction_type, target_user_id)
                except Exception as e:
                    print(f"Error en reacción {cmd}: {e}")

        # --- COMANDOS AVANZADOS DE TELETRANSPORTE ---
        if msg in ["!tpbot", "!comebot"] and is_admin:
            room_users = (await self.highrise.get_room_users()).content
            for u, pos in room_users:
                if u.id == user.id:
                    await self.highrise.teleport(self.bot_id, pos)
                    await self.highrise.chat(f"📍 Bot teletransportado a @{user.username}")
                    break
            return

        if msg.startswith(("!summon ", "!bring ")) and is_admin and len(args) > 1:
            target_search = args[1].replace("@", "").lower()
            room_users = (await self.highrise.get_room_users()).content
            admin_pos = None
            target_user = None

            for u, pos in room_users:
                if u.id == user.id:
                    admin_pos = pos
                if u.username.lower() == target_search:
                    target_user = u

            if admin_pos and target_user:
                await self.highrise.teleport(target_user.id, admin_pos)
                await self.highrise.chat(f"✨ @{target_user.username} fue teletransportado hacia @{user.username}")
            return

        if msg.startswith("!goto ") and is_admin and len(args) > 1:
            target_search = args[1].replace("@", "").lower()
            room_users = (await self.highrise.get_room_users()).content
            for u, pos in room_users:
                if u.username.lower() == target_search:
                    await self.highrise.teleport(user.id, pos)
                    await self.highrise.chat(f"✨ Teletransportado hacia @{u.username}")
                    break
            return

        # --- POSICIÓN FIJA DEL BOT (Solo Owner) ---
        if msg == "!setbot" and is_owner:
            room_users = (await self.highrise.get_room_users()).content
            for u, pos in room_users:
                if u.id == user.id:
                    self.bot_fixed_pos = {'x': pos.x, 'y': pos.y, 'z': pos.z}
                    await self.highrise.chat("📍 Posición fija del bot actualizada.")
                    break

        # --- COMANDOS DE MODERACIÓN DE AUDIENCIA ---
        if is_admin:
            if msg.startswith("!kick ") and len(args) > 1:
                target_search = args[1].replace("@", "").lower()
                room_users = (await self.highrise.get_room_users()).content
                for u, _ in room_users:
                    if u.username.lower() == target_search:
                        await self.highrise.moderate_room(u.id, "kick")
                        await self.highrise.chat(f"🚪 @{u.username} fue expulsado.")
                        break

            elif msg.startswith("!mute ") and len(args) > 1:
                target_search = args[1].replace("@", "").lower()
                duration = int(args[2]) if len(args) > 2 and args[2].isdigit() else 5
                room_users = (await self.highrise.get_room_users()).content
                for u, _ in room_users:
                    if u.username.lower() == target_search:
                        self.muted_users[u.id] = time.time() + (duration * 60)
                        await self.highrise.chat(f"🤫 @{u.username} ha sido silenciado por {duration} min.")
                        break

            elif msg.startswith("!unmute ") and len(args) > 1:
                target_search = args[1].replace("@", "").lower()
                room_users = (await self.highrise.get_room_users()).content
                for u, _ in room_users:
                    if u.username.lower() == target_search:
                        if u.id in self.muted_users: del self.muted_users[u.id]
                        await self.highrise.chat(f"🔊 @{u.username} ya no está silenciado.")
                        break

        # --- GESTIÓN DE PORTALES Y PUNTOS TP ---
        if is_admin:
            if msg == "!flash on":
                self.flash_enabled = True
                await self.highrise.chat("⚡ Portales Flash TP activados (verticales).")

            elif msg == "!flash off":
                self.flash_enabled = False
                await self.highrise.chat("🛑 Portales Flash TP desactivados.")

            elif msg.startswith("!set ") and len(args) > 1:
                zone = args[1].lower()
                room_users = (await self.highrise.get_room_users()).content
                for u, pos in room_users:
                    if u.id == user.id:
                        self.locations[zone] = {'x': pos.x, 'y': pos.y, 'z': pos.z}
                        if zone == "vip": self.vip_zone_pos = self.locations[zone]
                        await self.highrise.chat(f"📍 Punto '{zone}' guardado correctamente.")
                        break

            elif msg.startswith("!del ") and len(args) > 1:
                zone = args[1].lower()
                if zone in self.locations:
                    del self.locations[zone]
                    if zone == "vip": self.vip_zone_pos = None
                    await self.highrise.chat(f"🗑️ Punto '{zone}' eliminado.")

        # --- TELETRANSPORTE A PUNTOS GUARDADOS (Soporta `!lugar @user`) ---
        if msg.startswith("!"):
            cmd_name = args[0][1:].lower()
            if cmd_name in self.locations:
                target_user_id = user.id
                target_username = user.username

                if len(args) > 1 and is_admin:
                    target_search = args[1].replace("@", "").lower()
                    room_users = (await self.highrise.get_room_users()).content
                    for u, _ in room_users:
                        if u.username.lower() == target_search:
                            target_user_id = u.id
                            target_username = u.username
                            break

                is_target_vip = (target_username.lower() == self.owner.lower()) or \
                                (target_username.lower() in [a.lower() for a in self.admins]) or \
                                (target_username.lower() in [v.lower() for v in self.vips])

                if cmd_name == "vip" and not is_target_vip:
                    await self.highrise.send_whisper(user.id, f"⛔ @{target_username} no tiene acceso VIP.")
                    return

                loc = self.locations[cmd_name]
                try:
                    await self.highrise.teleport(target_user_id, Position(loc['x'], loc['y'], loc['z']))
                except Exception as e:
                    print(f"Error TP: {e}")

        # --- COMANDOS DE MENSAJES ---
        if is_admin:
            if msg.startswith("!setwelcome ") and len(args) > 1:
                self.welcome_message = " ".join(args[1:])
                await self.highrise.chat("✅ Bienvenida actualizada.")
            elif msg == "!resetwelcome":
                self.welcome_message = "Bienvenido/a a la sala."
                await self.highrise.chat("✅ Bienvenida reseteada.")
            elif msg.startswith("!setpromotext ") and len(args) > 1:
                self.promo_message = " ".join(args[1:])
                await self.highrise.chat("✅ Anuncio actualizado.")
            elif msg == "!resetpromo":
                self.promo_message = ""
                await self.highrise.chat("✅ Anuncio vaciado.")
            elif msg.startswith("!setpromotime ") and len(args) > 1 and args[1].isdigit():
                minutes = int(args[1])
                self.promo_interval = max(60, minutes * 60)
                await self.highrise.chat(f"⏰ Anuncio cada {minutes} min.")

        # --- GESTIÓN VIP MANUAL ---
        if is_admin:
            if msg.startswith("!vip ") and len(args) > 1 and args[1] not in ["admin", "tp"]:
                target = args[1].replace("@", "")
                if target in self.vips:
                    self.vips.remove(target)
                    await self.highrise.chat(f"❌ @{target} ya no es VIP.")
                else:
                    self.vips.append(target)
                    await self.highrise.chat(f"💎 @{target} ahora es VIP.")

            elif msg == "!vips":
                await self.highrise.send_whisper(user.id, f"📋 VIPs: {', '.join(self.vips) if self.vips else 'Ninguno'}")

        # --- BUCLADOR DE EMOTES ---
        if msg in ["!stop", "!stopdance"]:
            if user.id in self.active_loops:
                self.active_loops[user.id].cancel()
                del self.active_loops[user.id]
            await self.highrise.send_emote("idle-sleep", user.id)
            return

        if msg.isdigit():
            num = int(msg)
            if 1 <= num <= len(ALL_EMOTES):
                await self.start_emote_loop(user.id, ALL_EMOTES[num - 1])
                return

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

if __name__ == "__main__":
    from highrise.__main__ import main
    while True:
        try:
            print("🤖 Servicio DJBot iniciado...")
            main()
        except Exception as e:
            print(f"⚠️ Error de conexión: {e}")
            time.sleep(5)
