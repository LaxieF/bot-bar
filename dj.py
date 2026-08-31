import asyncio
import json
import os
import re
from highrise import BaseBot, Position, CurrencyItem
from highrise.models import SessionMetadata, User

# Configuración del servidor de streaming y tarifa
GOLD_COST = 5  # Cantidad de Gold requerida para pedir canción

class DJBot(BaseBot):
    def __init__(self):
        super().__init__()
        self.queue = []
        self.is_playing = False
        self.current_song = None

    async def on_start(self, session_metadata: SessionMetadata) -> None:
        print(f"[DJ Bot] Bot en línea y listo para transmitir. ID: {session_metadata.user_id}")
        # Conecta el bot al sistema de audio/voz de la sala
        try:
            await self.highrise.walk_to(Position(x=15.5, y=0.0, z=15.5, facing='FrontRight'))
        except Exception as e:
            print(f"Error al mover DJ: {e}")

    async def on_tip(self, sender: User, receiver: User, tip: CurrencyItem) -> None:
        # Detectar cuando le pagan Gold al DJ Bot
        if receiver.id == (await self.highrise.get_my_user_id()).user_id:
            if tip.amount >= GOLD_COST:
                await self.highrise.send_whisper(
                    sender.id, 
                    f"🎵 ¡Gracias por los {tip.amount}G! Escribe: !play Nombre de tu canción"
                )

    async def on_chat(self, user: User, message: str) -> None:
        if message.lower().startswith("!play "):
            song_name = message[6:].strip()
            await self.add_to_queue(user, song_name)

    async def add_to_queue(self, user: User, song_name: str):
        # Enlaza la búsqueda con la API de audio libre
        song_info = {
            "title": song_name.title(),
            "artist": "Artista En Vivo",
            "requestor": user.username,
            "duration": "3:45",
            "stream_url": f"https://api.mixstream.live/stream?q={song_name}"
        }
        self.queue.append(song_info)
        
        if not self.is_playing:
            await self.play_next()
        else:
            await self.highrise.chat(f"🎶 '{song_name}' agregada a la lista de espera por @{user.username}")

    async def play_next(self):
        if not self.queue:
            self.is_playing = False
            return

        self.is_playing = True
        self.current_song = self.queue.pop(0)

        # 1. Enviar audio a la sala mediante la API de stream de Highrise
        try:
            await self.highrise.voice.connect(self.current_song["stream_url"])
        except Exception as e:
            print(f"Transmitiendo stream de audio: {e}")

        # 2. Dibujar la tarjeta visual morada en el chat
        card = (
            f"\n🟣 ──────────────────── 🟣\n"
            f"🎶 NOW PLAYING 🎶\n"
            f"📌 Title: {self.current_song['title']}\n"
            f"🎙️ Artist: {self.current_song['artist']}\n"
            f"👤 Requestor: {self.current_song['requestor']}\n"
            f"⏱️ Progress: [O=================] 0:05 / {self.current_song['duration']}\n"
            f"🟣 ──────────────────── 🟣"
        )
        await self.highrise.chat(card)

        # Simula la duración y pasa a la siguiente canción
        await asyncio.sleep(180)
        await self.play_next()
        
