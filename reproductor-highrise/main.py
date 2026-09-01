import asyncio
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse, Response
import yt_dlp

app = FastAPI()

# Aquí guardamos la canción que está sonando en la radio en tiempo real
RADIO_STATE = {
    "current_url": None,
    "current_title": "Estación de Radio de LaxieF"
}

ydl_opts = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'default_search': 'ytsearch',
    'source_address': '0.0.0.0'
}

async def stream_radio_broadcast():
    """Transmite en vivo continuamente lo que esté configurado en RADIO_STATE"""
    while True:
        if not RADIO_STATE["current_url"]:
            # Si no hay música pedida, transmite silencio para no desconectar la antena
            await asyncio.sleep(1)
            continue
            
        process = await asyncio.create_subprocess_exec(
            'ffmpeg', '-i', RADIO_STATE["current_url"], '-f', 'mp3', '-acodec', 'libmp3lame', '-ab', '128k', 'pipe:1',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL
        )
        
        while True:
            chunk = await process.stdout.read(4096)
            if not chunk:
                break
            yield chunk
            
        await asyncio.sleep(1)

# CORRECCIÓN PARA HIGHRISE: Acepta GET (para audio) y HEAD (para la verificación del juego)
@app.route("/", methods=["GET", "HEAD"])
async def get_live_broadcast(request):
    # Si Highrise solo está verificando que la URL existe (HEAD), respondemos con un OK vacío
    if request.method == "HEAD":
        return Response(status_code=200, media_type="audio/mpeg")
    # Si el juego ya pide reproducir el audio (GET), iniciamos la transmisión continua
    return StreamingResponse(stream_radio_broadcast(), media_type="audio/mpeg")

@app.get("/change_song")
async def change_song(q: str = Query(..., description="Cambiar canción de la antena")):
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(None, lambda: ydl.extract_info(f"ytsearch:{q}", download=False))
            if not info or 'entries' not in info or len(info['entries']) == 0:
                raise HTTPException(status_code=404, detail="No encontrada")
            
            video_data = info['entries']
            RADIO_STATE["current_url"] = video_data['url']
            RADIO_STATE["current_title"] = video_data.get('title', 'Desconocido')
            
        return {"status": "success", "playing": RADIO_STATE["current_title"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
