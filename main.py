from highrise import BaseBot, Position, User, CurrencyItem
import random

class AXIBot(BaseBot):
    def __init__(self):
        super().__init__()
        self.bot_id = None
        
        # --- 1. PERMISOS Y ROLES ---
        self.owners = ["LaxieF"]  # Escribe tu usuario exacto de Highrise sin @
        self.admins = []
        self.vips = []
        
        # --- 2. CONFIGURACIÓN Y MENSAJES ---
        self.welcome_message = "Bienvenido/a a Drunk Bar 🍺 Escribe !help / !ayuda para ver los comandos."
        self.locations = {}  # Guarda zonas: {"bar": Position(...), "vip": Position(...)}
        self.vip_zone_pos = None  # Almacena la coordenada de la Zona VIP
        self.vip_radius = 3.0    # Radio de seguridad en bloques
        self.spawn_pos = None     # Entrada de la sala para rebotar colados
        
        # --- 3. MODO FLASH INTELIGENTE (VERTICAL) ---
        self.flash_users = set() # Usuarios con !flash activo
        self.user_positions = {} # Registro histórico de posiciones

        # --- 4. DICCIONARIO AMPLIADO DE BAILES (Atajos 1-30) ---
        self.emotes = {
            "1": "dance-tiktok8", "2": "dance-singalong", "3": "dance-russian",
            "4": "dance-poptart", "5": "dance-pennywise", "6": "dance-macarena",
            "7": "dance-weird", "8": "emote-superpose", "9": "emote-frog",
            "10": "dance-shoppingcart", "11": "dance-tiktok2", "12": "dance-duckwalk",
            "13": "emote-lust", "14": "dance-wrong", "15": "dance-anime",
            "16": "emote-pose1", "17": "dance-icecream", "18": "dance-zombieland",
            "19": "dance-floss", "20": "emote-sleigh", "21": "dance-touch",
            "22": "dance-aerobics", "23": "dance-smoothwalk", "24": "dance-hyped",
            "25": "dance-jinglebell", "26": "emote-celebration", "27": "dance-kpop",
            "28": "dance-handsup", "29": "dance-breakdance", "30": "dance-vogue"
        }

    async def on_start(self, session_metadata) -> None:
        self.bot_id = session_metadata.user_id
        print("🚀 AXIBot conectado con Roles, TPs, Flash Vertical, Anti-Colados VIP y ORO.")

    async def on_user_join(self, user: User, position: Position) -> None:
        if not self.spawn_pos and hasattr(position, 'x'):
            self.spawn_pos = position
        await self.highrise.chat(f"@{user.username} {self.welcome_message}")

    async def on_tip(self, sender: User, receiver: User, tip: CurrencyItem) -> None:
        # Agradecimiento público cuando alguien da oro en la sala
        if receiver.id == self.bot_id:
            await self.highrise.chat(f"🎉 ¡Muchísimas gracias @{sender.username} por la propina de {tip.amount} de oro! 🪙")

    async def on_user_move(self, user: User, pos: Position) -> None:
        username_lower = user.username.lower()

        # A) MODULO FLASH VERTICAL INTELIGENTE
        if user.id in self.flash_users:
            old_pos = self.user_positions.get(user.id)
            if old_pos and hasattr(pos, 'y') and hasattr(old_pos, 'y'):
                # Detecta si hubo un cambio vertical significativo (salto de piso)
                if abs(pos.y - old_pos.y) >= 1.5:
                    await self.highrise.teleport(user.id, Position(pos.x, pos.y, pos.z, getattr(pos, 'facing', 'FrontRight')))
            self.user_positions[user.id] = pos

        # B) SEGURIDAD Y REBOTE EN ZONA VIP
        if self.vip_zone_pos and username_lower not in [o.lower() for o in self.owners] and username_lower not in [a.lower() for a in self.admins] and username_lower not in [v.lower() for v in self.vips]:
            # Calcular distancia 3D a la zona VIP
            dx = pos.x - self.vip_zone_pos.x
            dy = pos.y - self.vip_zone_pos.y
            dz = pos.z - self.vip_zone_pos.z
            distSq = dx*dx + dy*dy + dz*dz

            if distSq <= (self.vip_radius * self.vip_radius):
                # Regresar al colado a la entrada y avisarle por mensaje privado
                target_dest = self.spawn_pos if self.spawn_pos else Position(0, 0, 0)
                await self.highrise.teleport(user.id, target_dest)
                await self.highrise.send_whisper(user.id, "⛔ No tienes acceso a la Zona VIP. Habla con el dueño para adquirir tu pase.")

    async def on_chat(self, user: User, message: str) -> None:
        msg = message.strip().lower()
        args = msg.split()
        username_lower = user.username.lower()

        # -------------------------------------------------------------
        # 1. ATAJO RÁPIDO DE BAILES (Número directo 1 a 30)
        # -------------------------------------------------------------
        if msg in self.emotes:
            try:
                await self.highrise.send_emote(self.emotes[msg], user.id)
            except Exception as e:
                print(f"Error emote: {e}")
            return

        # -------------------------------------------------------------
        # 2. SISTEMA MENÚ HELP MULTI-IDIOMA
        # -------------------------------------------------------------
        if msg in ["!help", "!ayuda", "!ajuda"]:
            if msg == "!ayuda":
                menu = "✨ **MENÚ PRINCIPAL DE AXIBot** ✨\n• !ayuda bailes\n• !ayuda tp\n• !ayuda vip\n• !ayuda admin"
            elif msg == "!ajuda":
                menu = "✨ **MENU PRINCIPAL AXIBot** ✨\n• !ajuda dancas\n• !ajuda tp\n• !ajuda vip\n• !ajuda admin"
            else:
                menu = "✨ **AXIBot MAIN MENU** ✨\n• !help dances\n• !help tp\n• !help vip\n• !help admin"
            await self.highrise.send_whisper(user.id, menu)
            return

        # Sub-menús detallados de ayuda
        if msg in ["!ayuda bailes", "!help dances", "!ajuda dancas"]:
            await self.highrise.send_whisper(user.id, "💃 **BAILES:**\nEscribe un número del 1 al 30 o usa !dance [id_oficial]. Ej: !dance dance-tiktok8 | !stop")
            return
        elif msg in ["!ayuda tp", "!help tp"]:
            zones = ", ".join([f"!{z}" for z in self.locations.keys()]) if self.locations else "Ninguna configurada."
            await self.highrise.send_whisper(user.id, f"📍 **TELETRANSPORTES:**\nComandos directos disponibles: {zones}")
            return

        # -------------------------------------------------------------
        # 3. EJECUCIÓN DE CUALQUIERA DE LOS 200+ EMOTES
        # -------------------------------------------------------------
        if msg.startswith("!dance "):
            emote_name = args[1]
            await self.highrise.send_emote(emote_name, user.id)
        elif msg in ["!stop", "!stopdance"]:
            await self.highrise.send_emote("emote-pose1", user.id)

        # -------------------------------------------------------------
        # 4. ATAJOS DIRECTOS DE TP (Ejemplo: escribir !bar, !vip, !pista)
        # -------------------------------------------------------------
        if msg.startswith("!") and len(msg) > 1:
            clean_cmd = msg[1:]
            if clean_cmd in self.locations:
                dest = self.locations[clean_cmd]
                await self.highrise.teleport(user.id, Position(dest.x, dest.y, dest.z, dest.facing))
                return

        # -------------------------------------------------------------
        # 5. COMANDOS DE EXCLUSIVOS DE DUEÑO Y ADMINISTRADORES
        # -------------------------------------------------------------
        is_owner = username_lower in [o.lower() for o in self.owners]
        is_admin = is_owner or username_lower in [a.lower() for a in self.admins]

        if is_admin:
            # Activar / Desactivar Modo Flash Vertical
            if msg == "!flash":
                if user.id in self.flash_users:
                    self.flash_users.remove(user.id)
                    await self.highrise.send_whisper(user.id, "⚡ Modo Flash desactivado.")
                else:
                    self.flash_users.add(user.id)
                    await self.highrise.send_whisper(user.id, "⚡ Modo Flash Vertical activado. Toca pisos altos para teletransportarte.")

            # Guardar Zonas de TP (Ejemplo: !set bar, !set vip)
            elif msg.startswith("!set ") and len(args) > 1:
                zone_name = args[1].lower()
                try:
                    room_users = (await self.highrise.get_room_users()).content
                    for u, pos in room_users:
                        if u.id == user.id:
                            self.locations[zone_name] = pos
                            if zone_name == "vip":
                                self.vip_zone_pos = pos
                            await self.highrise.chat(f"📍 Zona '{zone_name}' guardada exitosamente.")
                            return
                except Exception as e:
                    print(f"Error set zone: {e}")

            # Control y Movimiento del Bot
            elif msg in ["!tpbot", "!ven", "!come"]:
                try:
                    room_users = (await self.highrise.get_room_users()).content
                    for u, pos in room_users:
                        if u.id == user.id:
                            await self.highrise.teleport(self.bot_id, Position(pos.x, pos.y, pos.z, pos.facing))
                            return
                except Exception as e:
                    print(f"Error TP Bot: {e}")

            elif msg.startswith("!botwalk ") and len(args) > 1:
                target_zone = args[1].lower()
                if target_zone in self.locations:
                    dest = self.locations[target_zone]
                    await self.highrise.teleport(self.bot_id, Position(dest.x, dest.y, dest.z, dest.facing))

        # -------------------------------------------------------------
        # 6. COMANDOS BANCARIOS Y GESTIÓN EXCLUSIVA DEL DUEÑO
        # -------------------------------------------------------------
        if is_owner:
            # Cambiar Mensaje de Bienvenida en caliente
            if msg.startswith("!setwelcome "):
                self.welcome_message = message[12:].strip()
                await self.highrise.chat("✅ Mensaje de bienvenida actualizado.")

            # Consultar Billetera / Oro del Bot
            elif msg in ["!wallet", "!balance"]:
                try:
                    wallet = await self.highrise.get_wallet()
                    gold_amount = 0
                    for item in wallet.content:
                        if item.type == 'gold':
                            gold_amount = item.amount
                    await self.highrise.send_whisper(user.id, f"🪙 Balance actual del bot: {gold_amount} de oro.")
                except Exception as e:
                    print(f"Error al obtener wallet: {e}")

            # Dar permisos de VIP / Admin
            elif msg.startswith("!addvip ") and len(args) > 1:
                target = args[1].replace("@", "")
                if target not in self.vips:
                    self.vips.append(target)
                    await self.highrise.chat(f"👑 @{target} ahora tiene acceso VIP.")

            elif msg.startswith("!addadmin ") and len(args) > 1:
                target = args[1].replace("@", "")
                if target not in self.admins:
                    self.admins.append(target)
                    await self.highrise.chat(f"🛡️ @{target} ahora es Administrador/a.")
        
