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

threading.Thread(target=run_http_server, daemon=True).start()

print("Iniciando Bot DJ (Música)...")
subprocess.Popen([sys.executable, "dj.py"])

print("Iniciando Bot Principal (Barra/Moderación)...")
subprocess.Popen([sys.executable, "main.py"])

while True:
    time.sleep(60)
    
