import asyncio
import json
import os
import urllib.parse
import aiohttp
from highrise import BaseBot, Position, CurrencyItem
from highrise.models import SessionMetadata, User

PRECIO_DEL_ORO = 5  
MUSIC_API_URL = "https://highrise-music-server.onrender.com"

class DJBot(BaseBot):
    def __init__(self):
        super().__init__()
        self.cola = []
        self.esta_jugando = False
        self.cancion_actual = None

    async def on_start(self, session_metadata: SessionMetadata) -> None:
        print("[DJ Bot] Bot activo y listo.")

    async def on_tip(self, sender: User, receiver: User, tip: CurrencyItem) -> None:
        bot_id = await self.highrise.get_my_user_id()
        if receiver.id == bot_id:
            if tip.amount >= PRECIO_DEL_ORO:
                await self.highrise.send_whisper(
                    sender.id,
                    f"🎵 ¡Gracias por las {tip.amount} monedas! Usa !play <canción> para pedir tu tema."
                )

    async def on_chat(self, user: User, message: str) -> None:
        if message.lower().startswith("!play "):
            nombre_cancion = message[6:].strip()
            await self.agregar_a_la_cola(user, nombre_cancion)

    async def agregar_a_la_cola(self, user: User, nombre_cancion: str):
        await self.highrise.chat(f"🔎 Buscando '{nombre_cancion}'...")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{MUSIC_API_URL}/play", 
                    json={"query": nombre_cancion}, 
                    timeout=aiohttp.ClientTimeout(total=120)
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        raw_dur = data.get("duration")
                        try:
                            duracion_seg = int(raw_dur) if raw_dur is not None else 180
                        except (ValueError, TypeError):
                            duracion_seg = 180

                        minutos = duracion_seg // 60
                        segundos = duracion_seg % 60
                        duracion_str = f"{minutos}:{segundos:02d}"

                        # Enlace corto y limpio para la radio
                        encoded_query = urllib.parse.quote(nombre_cancion)
                        short_stream_url = f"{MUSIC_API_URL}/stream?query={encoded_query}"

                        informacion_cancion = {
                            "titulo": str(data.get("title") or nombre_cancion.title()),
                            "solicitante": user.username,
                            "solicitante_id": user.id,
                            "duracion": duracion_str,
                            "duracion_seg": duracion_seg,
                            "stream_url": short_stream_url
                        }

                        self.cola.append(informacion_cancion)

                        if not self.esta_jugando:
                            await self.reproducir_siguiente()
                        else:
                            await self.highrise.chat(f"🎵 '{informacion_cancion['titulo']}' agregada a la cola.")
                    else:
                        await self.highrise.chat("❌ No encontré esa canción.")

        except asyncio.TimeoutError:
            await self.highrise.chat("⚠️ El servidor tardó demasiado en responder.")
        except Exception as e:
            print(f"Error en dj.py: {e}")
            await self.highrise.chat("❌ Error al procesar la respuesta.")

    async def reproducir_siguiente(self):
        if not self.cola:
            self.esta_jugando = False
            self.cancion_actual = None
            return

        self.esta_jugando = True
        self.cancion_actual = self.cola.pop(0)

        # Anuncio público en la sala
        tarjeta = (
            f"\n🟣 ────────────────────── 🟣\n"
            f"🎶 REPRODUCIENDO AHORA 🎶\n"
            f"📌 Título: {self.cancion_actual['titulo']}\n"
            f"👤 Pedida por: {self.cancion_actual['solicitante']}\n"
            f"⏱️ Duración: {self.cancion_actual['duracion']}\n"
            f"🟣 ────────────────────── 🟣"
        )
        await self.highrise.chat(tarjeta)

        # Susurro con enlace corto y limpio
        link_audio = self.cancion_actual.get("stream_url")
        if link_audio:
            try:
                await self.highrise.send_whisper(
                    self.cancion_actual["solicitante_id"],
                    f"🔗 Enlace corto para la radio:\n{link_audio}"
                )
            except Exception as w_err:
                print(f"Error enviando susurro: {w_err}")

        tiempo_espera = self.cancion_actual.get("duracion_seg", 180)
        await asyncio.sleep(tiempo_espera)
        
        await self.reproducir_siguiente()
                    
