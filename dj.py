import requests

def buscar_musica_api(nombre_cancion):
    """
    Busca una canción en una API de conversión externa y devuelve una URL .mp3
    directa y compatible con la casilla de Highrise.
    """
    # Usamos una API pública de conversión (puedes cambiar este endpoint si deja de funcionar)
    url_api = f"https://vevo.guru{nombre_cancion}"
    
    try:
        response = requests.get(url_api, timeout=10)
        if response.status_code == 200:
            datos = response.json()
            # Validamos que la API haya encontrado resultados válidos
            if "results" in datos and len(datos["results"]) > 0:
                # Extraemos el enlace de transmisión de audio directo (.mp3)
                url_directa_mp3 = datos["results"][0]["download_url"]
                return url_directa_mp3
        return None
    except Exception as e:
        print(f"Error al conectar con la API de música: {e}")
        return None
        
