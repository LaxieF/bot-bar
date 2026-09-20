import os
import asyncio
import subprocess
from highrise import BaseBot
from highrise.__main__ import BotDefinition, main
from dotenv import load_dotenv

load_dotenv()
ROOM_ID = os.getenv("ROOM_ID")
BOT_TOKEN = os.getenv("BOT_TOKEN")

class DJBot(BaseBot):
    async def on_start(self, session_metadata: any) -> None:
        print("🎧 DJBot conectado y listo para la música.", flush=True)

    async def on_chat(self, user: any, message: str) -> None:
        msg = message.strip()
        msg_lower = msg.lower()

        if msg_lower == "!help":
            await self.highrise.chat(f"@{user.username} 📜 Comandos: !play | !stop")

        elif msg_lower.startswith("!play"):
            await self.highrise.chat(f"@{user.username} 🎶 ¡Encendiendo la radio en vivo de la sala!")
            subprocess.Popen("pkill -f ffmpeg", shell=True)
            audio_url = "https://radiorevolt.no"
            cmd = f"ffmpeg -re -i \"{audio_url}\" -codec:a libmp3lame -b:a 128k -content_type audio/mpeg -f mp3 icecast://localhost:5000/stream"
            subprocess.Popen(cmd, shell=True)

        elif msg_lower == "!stop":
            subprocess.Popen("pkill -f ffmpeg", shell=True)
            await self.highrise.chat(f"@{user.username} 🛑 Radio apagada.")

if __name__ == "__main__":
    definitions = [BotDefinition(DJBot(), ROOM_ID, BOT_TOKEN)]
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(definitions))
    
