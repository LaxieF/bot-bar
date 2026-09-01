import asyncio
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse
import yt_dlp

app = FastAPI()

ydl_opts = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'default_search': 'ytsearch',
    'source_address': '0.0.0.0'
}

async def stream_audio(url: str):
    process = await asyncio.create_subprocess_exec(
        'ffmpeg', '-i', url, '-f', 'mp3', '-acodec', 'libmp3lame', '-ab', '128k', 'pipe:1',
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.DEVNULL
    )
    while True:
        chunk = await process.stdout.read(4096)
        if not chunk:
            break
        yield chunk

@app.get("/stream")
async def get_stream(q: str = Query(..., description="Cancion")):
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(None, lambda: ydl.extract_info(f"ytsearch:{q}", download=False))
            if not info or 'entries' not in info or len(info['entries']) == 0:
                raise HTTPException(status_code=404, detail="No encontrada")
            video_data = info['entries']
            audio_url = video_data['url']
        return StreamingResponse(stream_audio(audio_url), media_type="audio/mpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
