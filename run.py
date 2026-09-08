import subprocess
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")
    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

def run_http_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=run_http_server, daemon=True).start()

print("--- INICIANDO BOTS EN HIGHRISE ---", flush=True)

# PON AQUÍ TU ID DE SALA Y TOKENS REALES ENTRE LAS COMILLAS
ROOM_ID = "66137b812eb7852780780ace"
TOKEN_MAIN = "6d32cf535a03072a44a9e609f861d619048510e2bca71917f322b45b18384339"
TOKEN_DJ = "d56c280270fa345592ce1ed994ae8ade013e9fa9c48ae744e03eef57278f87a0"

# Ejecuta los bots pasando los tokens directamente
p1 = subprocess.Popen(["python", "-m", "highrise", "main:AXIBot", ROOM_ID, TOKEN_MAIN])
p2 = subprocess.Popen(["python", "-m", "highrise", "dj:DJBot", ROOM_ID, TOKEN_DJ])

p1.wait()
p2.wait()
