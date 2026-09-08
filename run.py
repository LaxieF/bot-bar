import multiprocessing
import os
import subprocess

def arrancar_bot_principal():
    # Render ejecutará tu archivo de moderación principal
    print("Iniciando Bot Principal (Barra/Moderación)...")
    subprocess.run(["python", "main.py"])

def arrancar_bot_dj():
    # Render ejecutará tu archivo de música en paralelo
    print("Iniciando Bot DJ (Música)...")
    subprocess.run(["python", "dj.py"])

if __name__ == "__main__":
    # Creamos dos procesos independientes para que corran juntos
    proceso_principal = multiprocessing.Process(target=arrancar_bot_principal)
    proceso_dj = multiprocessing.Process(target=arrancar_bot_dj)
    
    # Arrancamos ambos
    proceso_principal.start()
    proceso_dj.start()
    
    # Los mantenemos vivos compartiendo el mismo servicio de Render
    proceso_principal.join()
    proceso_dj.join()
  
