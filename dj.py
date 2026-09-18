import os
import asyncio
import requests
from highrise import BaseBot, Position
from flask import Flask
from threading import Thread

# Mini servidor web obligatorio para mantener el bot activo
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
        # ⚠️ Cambia "TuNombreDeUsuario" por tu usuario exacto en Highrise (es el Dueño principal)
        self.owner_username = "TuNombreDeUsuario".lower()
        self.admins = {self.owner_username} # Lista de administradores autorizados
        self.home_position = None # Aquí se guardará la posición fija del bot
        self.current_announcement = "🎧 ¡Bienvenidos! Usa !play [nombre de canción] por 5 de oro para pedir tu música."
        self.is_running_loop = False

    async def on_start(self, session_metadata) -> None:
        self.bot_id = session_metadata.user_id
        print("🎧 DJBot conectado y listo para la música.", flush=True)
        
        # Iniciar el bucle de mensajes automáticos si no está activo
        if not self.is_running_loop:
            self.is_running_loop = True
            asyncio.create_task(self.auto_announcement_loop())

    async def auto_announcement_loop(self):
        """Manda el mensaje de anuncio a la sala cada 5 minutos (300 segundos)"""
        while True:
            await asyncio.sleep(300) # 300 segundos = 5 minutos (puedes cambiarlo si quieres)
            try:
                if self.current_announcement:
                    await self.highrise.chat(self.current_announcement)
            except Exception as e:
                print(f"Error en anuncio automático: {e}", flush=True)

    def is_admin(self, username: str) -> bool:
        """Verifica si un usuario es administrador o el dueño"""
        return username.lower() in self.admins

    async def on_chat(self, user, message: str) -> None:
        msg = message.strip()
        msg_lower = msg.lower()
        username = user.username.lower()

        # ==================== COMANDOS PÚBLICOS ====================
        
        # 1. Comando !play (Público para todos)
        if msg_lower.startswith("!play "):
            busqueda = msg[6:].strip()
            if not busqueda:
                await self.highrise.chat(f"@{user.username} ⚠️ Por favor escribe el nombre de una canción después de !play")
                return

            await self.highrise.chat(f"@{user.username} 🎶 Buscando: {busqueda} (Recuerda asegurar tus 5 de oro).")
            
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
                        await self.highrise.chat(f"▶️ Reproduciendo pedido de @{user.username}: {titulo}")
                    else:
                        await self.highrise.chat("❌ El servidor no devolvió una URL válida.")
                else:
                    await self.highrise.chat("❌ No se pudo procesar la canción en el servidor.")
                    
            except Exception as e:
                print(f"Error conectando a VPS: {e}", flush=True)
                await self.highrise.chat("⚠️ Error de conexión con el servidor de música.")

        # 2. Comando !help (Público)
        elif msg_lower == "!help":
            help_text = (
                "📜 Comandos del DJ:\n"
                "- !play [canción] (Pide música por 5 de oro)\n"
                "- !tpdj (Mueve al bot a tu posición)\n"
                "- !help (Muestra esta ayuda)"
            )
            await self.highrise.chat(help_text)

        # ==================== COMANDOS DE MOVIMIENTO ====================

        # 3. Comando !tpdj (Mueve al bot a donde estás)
        elif msg_lower == "!tpdj":
            try:
                room_users = (await self.highrise.get_room_users()).content
                for u, pos in room_users:
                    if u.username.lower() == username:
                        x = getattr(pos, "x", 0)
                        y = getattr(pos, "y", 0)
                        z = getattr(pos, "z", 0)
                        facing = getattr(pos, "facing", "FrontRight")
                        await self.highrise.teleport(self.bot_id, Position(x, y, z, facing))
                        await self.highrise.chat(f"📍 ¡Me he movido a tu posición, {user.username}!")
                        return
            except Exception as e:
                print(f"Error TP DJBot: {e}", flush=True)

        # 4. Comando !sethome (Guarda la posición actual como base del bot)
        elif msg_lower == "!sethome":
            if not self.is_admin(username):
                await self.highrise.chat(f"@{user.username} ❌ No tienes permisos para usar este comando.")
                return
            try:
                room_users = (await self.highrise.get_room_users()).content
                for u, pos in room_users:
                    if u.username.lower() == username:
                        self.home_position = pos
                        await self.highrise.chat(f"🏠 ¡Posición base guardada correctamente!")
                        return
            except Exception as e:
                print(f"Error guardando home: {e}", flush=True)

        # ==================== COMANDOS PROTEGIDOS (SOLO ADMINS) ====================

        # 5. Comando !stop (Detiene la música - Solo Admins)
        elif msg_lower == "!stop":
            if not self.is_admin(username):
                await self.highrise.chat(f"@{user.username} ❌ Solo los administradores pueden detener la música.")
                return
            await self.highrise.chat(f"⏹️ Música detenida por el administrador @{user.username}.")
            # Aquí puedes añadir la petición HTTP a tu servidor para detener el stream si lo requieres.

        # 6. Comando !next (Salta de canción - Solo Admins)
        elif msg_lower == "!next":
            if not self.is_admin(username):
                await self.highrise.chat(f"@{user.username} ❌ Solo los administradores pueden saltar canciones.")
                return
            await self.highrise.chat(f"⏭️ Saltando canción por orden de @{user.username}...")
            # Aquí puedes añadir la petición HTTP a tu servidor para pasar al siguiente tema.

        # 7. Comando !mensaje (Modifica el anuncio automático - Solo Admins)
        elif msg_lower.startswith("!mensaje "):
            if not self.is_admin(username):
                await self.highrise.chat(f"@{user.username} ❌ Solo los administradores pueden cambiar el mensaje.")
                return
            nuevo_texto = message[9:].strip()
            if not nuevo_texto:
                await self.highrise.chat("⚠️ Debes escribir el nuevo texto para el mensaje.")
                return
            self.current_announcement = nuevo_texto
            await self.highrise.chat(f"💬 Anuncio actualizado correctamente:\n\"{self.current_announcement}\"")

        # 8. Comando !mod [usuario] (Agrega un nuevo moderador - Solo Dueño)
        elif msg_lower.startswith("!mod "):
            if username != self.owner_username:
                await self.highrise.chat(f"@{user.username} ❌ Solo el dueño principal puede agregar moderadores.")
                return
            nuevo_mod = message[5:].strip().lstrip("@").lower()
            if not nuevo_mod:
                await self.highrise.chat("⚠️ Escribe el nombre de usuario del nuevo moderador.")
                return
            self.admins.add(nuevo_mod)
            await self.highrise.chat(f"🛡️ ¡El usuario @{nuevo_mod} ahora es administrador del bot!")

# Arrancamos el servidor web en segundo plano
if __name__ == "__main__":
    t = Thread(target=run_web)
    t.daemon = True
    t.start()
