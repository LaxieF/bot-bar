import asyncio
import json
import os
import re
import aiohttp
from highrise import BaseBot, Position, CurrencyItem
from highrise.models import SessionMetadata, User

# Configuración del servidor de streaming y tarifa
PRECIO_DEL_ORO = 5  # Cantidad de oro requerida para pedir canción
MUSIC_API_URL = "https://highrise-music-server.onrender.com"

class DJBot(BaseBot):
    def __init__(self):
        super().__init__()
        self.cola = []
        self.esta_jugando = False
        self.cancion_actual = None

    async def on_start(self, session_metadata: SessionMetadata) -> None:
        print(f"[DJ Bot] Bot en línea y listo para reproducir música.")

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
        await self.highrise.chat(f"🔎 Buscando '{nombre_cancion}'...")

        try:
            # Consultamos la API de Render para obtener los datos de la canción
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{MUSIC_API_URL}/play", json={"query": nombre_cancion}, timeout=15) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Formateamos la duración
                        duracion_seg = data.get("duration", 180) or 180
                        minutos = duracion_seg // 60
                        segundos = duracion_seg % 60
                        duracion_str = f"{minutos}:{segundos:02d}"

                        informacion_cancion = {
                            "titulo": data.get("title", nombre_cancion.title()),
                            "solicitante": user.username,
                            "duracion": duracion_str,
                            "duracion_seg": duracion_seg,
                            "stream_url": data.get("stream_url")
                        }

                        self.cola.append(informacion_cancion)

                        if not self.esta_jugando:
                            await self.reproducir_siguiente()
                        else:
                            await self.highrise.chat(f"🎵 '{informacion_cancion['titulo']}' agregada a la cola.")
                    else:
                        await self.highrise.chat("❌ No encontré esa canción en YouTube.")
        except Exception as e:
            print(f"Error al conectar con la API de música: {e}")
            await self.highrise.chat("⚠️ El servidor de música no respondió a tiempo.")

    async def reproducir_siguiente(self):
        if not self.cola:
            # Si ya no hay más canciones, el bot frena de forma limpia
            self.esta_jugando = False
            self.cancion_actual = None
            return

        self.esta_jugando = True
        self.cancion_actual = self.cola.pop(0)

        # 1. Dibujar la tarjeta visual morada en el chat
        tarjeta = (
            f"\n🟣 ────────────────────── 🟣\n"
            f"🎶 SONANDO AHORA 🎶\n"
            f"📌 Título: {self.cancion_actual['titulo']}\n"
            f"👤 Solicitante: {self.cancion_actual['solicitante']}\n"
            f"⏱️ Duración: {self.cancion_actual['duracion']}\n"
            f"🟣 ────────────────────── 🟣"
        )
        await self.highrise.chat(tarjeta)

        # Espera el tiempo real de la canción antes de pasar a la siguiente
        tiempo_espera = self.cancion_actual.get("duracion_seg", 180)
        await asyncio.sleep(tiempo_espera)
        
        # Siguiente tema
        await self.reproducir_siguiente()
        
