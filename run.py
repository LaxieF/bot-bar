import subprocess
import time
import sys
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def run_http_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

# Iniciar servidor HTTP en un hilo
threading.Thread(target=run_http_server, daemon=True).start()

# Forzar a Python a no usar buffer (-u) para ver los prints e iniciar directo
print("--- INICIANDO BOTS EN HIGHRISE ---", flush=True)

p1 = subprocess.Popen([sys.executable, "-u", "dj.py"])
p2 = subprocess.Popen([sys.executable, "-u", "main.py"])

# Esperar a que los procesos se mantengan vivos
try:
    p1.wait()
    p2.wait()
except Exception as e:
    print(f"Error en ejecucion: {e}", flush=True)
    
