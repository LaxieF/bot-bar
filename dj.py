import asyncio
import json
import os
import re
import aiohttp
from highrise import BaseBot, Position, CurrencyItem
from highrise.models import SessionMetadata, User

# Configuración del servidor de streaming y tarifa
PRECIO_DEL_ORO = 5  # Cantidad de oro requerida para pedir canción

class DJBot(BaseBot):
    def __init__(self):
        super().__init__()
        self.cola = []
        self.esta_jugando = False
        self.cancion_actual = None

    async def on_start(self, session_metadata: SessionMetadata) -> None:
        print(f"[DJ Bot] Bot en línea y listo para reproducir música.")
        # Quitamos el walk_to automático para que el bot se quede quieto donde lo dejes 
        # y no salga corriendo a la esquina (0,0,0)

    async def on_tip(self, sender: User, receiver: User, tip: CurrencyItem) -> None:
        if receiver.id == (await self.highrise.get_my_user_id()):
            if tip.amount >= PRECIO_DEL_ORO:
                await self.highrise.send_whisper(
                    sender.id,
                    f"🎵 ¡Gracias por los {tip.amount} Gold! Usa !play <nombre de canción> para pedir tu tema."
                )

    async def on_chat(self, user: User, message: str) -> None:
        if message.lower().startswith("!play "):
            nombre_cancion = message[6:].strip()
            await self.agregar_a_la_cola(user, nombre_cancion)

    async def agregar_a_la_cola(self, user: User, nombre_cancion: str):
        termino_busqueda = nombre_cancion.replace(" ", "+")
        url_antena = f"https://onrender.com{termino_busqueda}"

        informacion_cancion = {
            "titulo": nombre_cancion.title(),
            "artista": "Artista En Vivo",
            "solicitante": user.username,
            "duracion": "3:45",
            "stream_url": url_antena
        }

        self.cola.append(informacion_cancion)

        if not self.esta_jugando:
            await self.reproducir_siguiente()
        else:
            await self.highrise.chat(f"🎵 '{nombre_cancion}' agregada a la cola.")

    async def reproducir_siguiente(self):
        if not self.cola:
            self.esta_jugando = False
            return

        self.esta_jugando = True
        self.cancion_actual = self.cola.pop(0)

        # 1. Cambiar la música en la antena usando peticiones asíncronas seguras (No traba al bot)
        try:
            termino = self.cancion_actual["titulo"].replace(" ", "+")
            url_cambio = f"https://onrender.com{termino}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url_cambio) as response:
                    await response.json()
                    
        except Exception as e:
            print(f"Error al cambiar la música en la antena: {e}")

        # 2. Dibujar la tarjeta visual morada en el chat
        tarjeta = (
            f"\n🟣 ────────────────────── 🟣\n"
            f"🎶 SONANDO AHORA 🎶\n"
            f"📌 Título: {self.cancion_actual['titulo']}\n"
            f"🎙️ Artista: {self.cancion_actual['artista']}\n"
            f"👤 Solicitante: {self.cancion_actual['solicitante']}\n"
            f"⏱️ Progreso: [0=================] 0:05 / {self.cancion_actual['duracion']}\n"
            f"🟣 ────────────────────── 🟣"
        )
        await self.highrise.chat(tarjeta)

        # Simula la duración y pasa a la siguiente canción
        await asyncio.sleep(180)
        await self.reproducir_siguiente()
                
