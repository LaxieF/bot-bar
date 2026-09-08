import requests

def buscar_musica_api(nombre_cancion):
    """
    Busca una canción en una API externa y devuelve una URL .mp3
    directa para que el bot la pegue en la sala de Highrise.
    """
    url_api = f"https://vevo.guru{nombre_cancion}"
    
    try:
        response = requests.get(url_api, timeout=10)
        if response.status_code == 200:
            datos = response.json()
            if "results" in datos and len(datos["results"]) > 0:
                # Extraemos el enlace limpio .mp3 que necesita Highrise
                url_directa_mp3 = datos["results"]["download_url"]
                return url_directa_mp3
        return None
    except Exception as e:
        print(f"Error al conectar con la API de música: {e}")
        return None
        
