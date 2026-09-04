import asyncio
import json
import os
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
            # Petición HTTP con timeout extendido
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{MUSIC_API_URL}/play", 
                    json={"query": nombre_cancion}, 
                    timeout=aiohttp.ClientTimeout(total=120)
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        duracion_seg = data.get("duration", 180) or 180
                        minutos = duracion_seg // 60
                        segundos = duracion_seg % 60
                        duracion_str = f"{minutos}:{segundos:02d}"

                        informacion_cancion = {
                            "titulo": data.get("title", nombre_cancion.title()),
                            "solicitante": user.username,
                            "solicitante_id": user.id,
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
                        await self.highrise.chat("❌ No encontré esa canción.")

        except asyncio.TimeoutError:
            await self.highrise.chat("⚠️ El servidor tardó demasiado en responder.")
        except Exception as e:
            print(f"Error en dj.py: {e}")
            await self.highrise.chat("❌ Error al procesar la solicitud.")

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

        # Susurro privado con el enlace directo
        link_audio = self.cancion_actual.get("stream_url")
        if link_audio:
            try:
                await self.highrise.send_whisper(
                    self.cancion_actual["solicitante_id"],
                    "🔗 Enlace para la radio:"
                )
                await asyncio.sleep(0.5)
                await self.highrise.send_whisper(
                    self.cancion_actual["solicitante_id"],
                    link_audio
                )
            except Exception as w_err:
                print(f"Error enviando susurro: {w_err}")

        tiempo_espera = self.cancion_actual.get("duracion_seg", 180)
        await asyncio.sleep(tiempo_espera)
        
        await self.reproducir_siguiente()
                
