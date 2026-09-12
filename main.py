from highrise import BaseBot, Position, User, CurrencyItem
import asyncio
import json
import sys
import os
import time

# --- REPOSITORIO DE EMOTES PARA EL BOT ---
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

# MAPA DE REACCIONES FLOTANTES OFICIALES DE HIGHRISE
REACTIONS = {
    "heart": "heart",
    "wink": "wink",
    "wave": "wave",
    "clap": "clap",
    "thumbs": "thumbs"
}

class AXIBot(BaseBot):
    def __init__(self):
        super().__init__()
        self.bot_id = None
        self.owner = "LaxieF"
        self.admins = []
        
        # VIPs persistentes guardados en disco
        self.vips = self.load_vips()
        
        # MENSAJES PERSONALIZABLES
        self.welcome_message = "Bienvenido/a a Drunk Bar 🍺 Escribe !ayuda o !help."
        self.promo_message = "🌟 ¡Consigue acceso VIP permanente enviando una propina de 500g al bot!"
        self.promo_interval = 300  # 5 minutos
        self.promo_active = True
        self.promo_task = None
        
        self.locations = {}
        self.vip_zone_pos = None
        self.vip_radius = 3.0
        self.spawn_pos = None
        
        self.active_loops = {}
        self.user_cooldowns = {}
        self.cooldown_time = 2.0

    # Carga y guardado de VIPs en disco
    def load_vips(self):
        try:
            if os.path.exists("vips.json"):
                with open("vips.json", "r") as f:
                    data = json.load(f)
                    print(f"📂 Lista VIP cargada: {len(data)} miembros.")
                    return data
            return []
        except Exception as e:
            print(f"Error cargando VIPs: {e}")
            return []

    def save_vips(self):
        try:
            with open("vips.json", "w") as f:
                json.dump(self.vips, f)
            print("💾 Lista VIP guardada con éxito.")
        except Exception as e:
            print(f"Error guardando VIPs: {e}")

    async def on_start(self, session_metadata) -> None:
        self.bot_id = session_metadata.user_id
        print(f"🎧 DJBot conectado y listo para la música.")
        if self.promo_active:
            self.promo_task = asyncio.create_task(self.run_promo_loop())

    async def on_user_join(self, user: User, position: Position) -> None:
        if not self.spawn_pos and hasattr(position, 'x'):
            self.spawn_pos = position
        try:
            await self.highrise.chat(f"@{user.username} {self.welcome_message}")
        except Exception as e:
            print(f"Error bienvenida: {e}")

    # Pago VIP por propina directa
    async def on_tip(self, sender: User, receiver: User, tip: CurrencyItem) -> None:
        if receiver.id == self.bot_id:
            print(f"💰 [PROPINA] @{sender.username} envió {tip.amount}g de oro.")
            await self.highrise.chat(f"🎉 ¡Gracias @{sender.username} por la propina de {tip.amount}g de oro! 🪙")
            
            if tip.amount >= 500:
                if sender.username not in self.vips:
                    self.vips.append(sender.username)
                    self.save_vips()
                    await self.highrise.chat(f"💎 ¡Felicidades @{sender.username}! Ahora eres miembro VIP permanente.")

    async def on_user_move(self, user: User, pos: Position) -> None:
        username_lower = user.username.lower()

        # Restricción de Zona VIP
        if self.vip_zone_pos and username_lower != self.owner.lower() and username_lower not in [a.lower() for a in self.admins] and username_lower not in [v.lower() for v in self.vips]:
            dx, dy, dz = pos.x - self.vip_zone_pos.x, pos.y - self.vip_zone_pos.y, pos.z - self.vip_zone_pos.z
            if (dx*dx + dy*dy + dz*dz) <= (self.vip_radius * self.vip_radius):
                target_dest = self.spawn_pos if self.spawn_pos else Position(0, 0, 0)
                await self.highrise.teleport(user.id, target_dest)
                await self.highrise.send_whisper(user.id, "⛔ Zona VIP restringida. Compra VIP enviando 500g al bot.")

    async def run_promo_loop(self):
        try:
            while self.promo_active:
                await asyncio.sleep(self.promo_interval)
                if self.promo_message:
                    await self.highrise.chat(self.promo_message)
        except asyncio.CancelledError:
            pass

    async def on_chat(self, user: User, message: str) -> None:
        msg = message.strip().lower()
        args = message.strip().split()
        username_lower = user.username.lower()

        is_owner = username_lower == self.owner.lower()
        is_admin = is_owner or username_lower in [a.lower() for a in self.admins]

        # Anti-Spam
        current_time = time.time()
        if not is_admin:
            if user.id in self.user_cooldowns:
                if current_time - self.user_cooldowns[user.id] < self.cooldown_time:
                    return
            self.user_cooldowns[user.id] = current_time

        # Reiniciar Bot
        if msg in ["!restart", "!reiniciar"] and is_owner:
            await self.highrise.chat("🔄 Reiniciando el bot...")
            os.execv(sys.executable, ['python'] + sys.argv)

        # Menús de Ayuda
        if msg in ["!ayuda", "!help", "/help"]:
            menu = (
                "<color=#F2C94C>✨ Categorías de Comandos: ✨</color>\n\n"
                "💃 <color=#E282B7>/help emotes</color>\n"
                "🚀 <color=#7CB9E8>/help tp</color>\n"
                "❤️ <color=#A892EE>/help react</color>\n"
                "💬 <color=#00FFFF>/help messages</color>\n"
                "🛡️ <color=#FF7F50>/help mod</color>"
            )
            await self.highrise.send_whisper(user.id, menu)
            return

        if msg in ["/help react", "!help react"]:
            text = "❤️ <color=#A892EE>**REACCIONES FLOTANTES**</color>\n• !heart @user\n• !wink @user\n• !wave @user\n• !clap @user\n• !thumbs @user"
            await self.highrise.send_whisper(user.id, text)
            return

        if msg in ["/help messages", "!help messages"] and is_admin:
            text = (
                "💬 <color=#00FFFF>**CONFIGURACIÓN DE MENSAJES**</color>\n"
                "• !setwelcome <texto> - Cambia bienvenida.\n"
                "• !setpromotext <texto> - Cambia anuncio.\n"
                "• !setpromotime <min> - Minutos entre anuncios.\n"
                "• !promoon / !promooff - Activa/Desactiva anuncios."
            )
            await self.highrise.send_whisper(user.id, text)
            return

        # Configuración de Mensajes
        if is_admin:
            if msg.startswith("!setwelcome ") and len(args) > 1:
                self.welcome_message = " ".join(args[1:])
                await self.highrise.chat("✅ Mensaje de bienvenida actualizado.")

            elif msg.startswith("!setpromotext ") and len(args) > 1:
                self.promo_message = " ".join(args[1:])
                await self.highrise.chat("✅ Mensaje promocional actualizado.")

            elif msg.startswith("!setpromotime ") and len(args) > 1 and args[1].isdigit():
                minutes = int(args[1])
                self.promo_interval = max(60, minutes * 60)
                await self.highrise.chat(f"⏰ Anuncio programado cada {minutes} minutos.")

            elif msg == "!promoon":
                self.promo_active = True
                if self.promo_task: self.promo_task.cancel()
                self.promo_task = asyncio.create_task(self.run_promo_loop())
                await self.highrise.chat("📢 Anuncios automáticos activados.")

            elif msg == "!promooff":
                self.promo_active = False
                if self.promo_task: self.promo_task.cancel()
                await self.highrise.chat("🛑 Anuncios automáticos desactivados.")

        # REACCIONES FLOTANTES SOBRE EL JUGADOR (react)
        if msg.startswith(("!heart", "!wink", "!wave", "!clap", "!thumbs")):
            cmd = msg.split()[0][1:]
            reaction_type = REACTIONS.get(cmd)
            
            if reaction_type:
                target_user_id = user.id
                target_name = user.username

                if len(args) > 1:
                    target_search = args[1].replace("@", "").lower()
                    try:
                        room_users = (await self.highrise.get_room_users()).content
                        for u, _ in room_users:
                            if u.username.lower() == target_search:
                                target_user_id = u.id
                                target_name = u.username
                                break
                    except Exception as e:
                        print(f"Error buscando usuario: {e}")

                try:
                    await self.highrise.react(reaction_type, target_user_id)
                except Exception as e:
                    print(f"Error enviando reacción: {e}")

        # Emotes en Bucle
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

        # Puntos TP Protegidos contra Bucle
        if is_admin and msg.startswith("!set ") and len(args) > 1:
            zone = args[1].lower()
            try:
                room_users = (await self.highrise.get_room_users()).content
                for u, pos in room_users:
                    if u.id == user.id:
                        self.locations[zone] = pos
                        if zone == "vip": self.vip_zone_pos = pos
                        await self.highrise.chat(f"📍 Punto '{zone}' guardado con éxito.")
                        break  # <--- Evita el spam/crash de la última vez
            except Exception as e:
                print(f"Error set: {e}")

        # Comandos de Gestión VIP
        if is_admin:
            if msg.startswith("!vip ") and len(args) > 1 and args[1] not in ["admin", "tp"]:
                target = args[1].replace("@", "")
                if target in self.vips:
                    self.vips.remove(target)
                    self.save_vips()
                    await self.highrise.chat(f"❌ @{target} ya no es VIP.")
                else:
                    self.vips.append(target)
                    self.save_vips()
                    await self.highrise.chat(f"💎 @{target} ahora es VIP.")

            elif msg == "!vips":
                await self.highrise.send_whisper(user.id, f"📋 VIPs guardados ({len(self.vips)}): {', '.join(self.vips) if self.vips else 'Ninguno'}")

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

# BUCLE DE INICIO Y RECONEXIÓN AUTOMÁTICA
if __name__ == "__main__":
    from highrise.__main__ import main
    while True:
        try:
            print("🤖 Servicio DJBot iniciado...")
            main()
        except Exception as e:
            print(f"⚠️ Error de conexión: {e}")
            time.sleep(5)
