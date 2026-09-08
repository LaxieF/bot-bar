import subprocess
import time
import sys

print("Iniciando Bot DJ (Música)...")
subprocess.Popen([sys.executable, "dj.py"])

print("Iniciando Bot Principal (Barra/Moderación)...")
subprocess.Popen([sys.executable, "main.py"])

# Mantiene el proceso vivo para que Render no se apague
while True:
    time.sleep(60)
    
