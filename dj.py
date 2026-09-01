    async def reproducir_siguiente(self):
        if not self.cola:
            self.esta_jugando = False
            return

        self.esta_jugando = True
        self.cancion_actual = self.cola.pop(0)

        # 1. Le ordenamos a tu servidor de Render que cambie la canción en la antena fija
        try:
            import urllib.request
            import urllib.parse
            
            termino = self.cancion_actual["titulo"].replace(" ", "+")
            # Cambiamos la canción en la central de Render
            url_cambio = f"https://onrender.com{termino}"
            
            # Hacemos la petición en segundo plano de forma asíncrona
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, lambda: urllib.request.urlopen(url_cambio).read())
            
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
        
