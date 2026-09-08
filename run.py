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

# Lanza los bots mediante el ejecutable oficial del SDK
p1 = subprocess.Popen(["python", "-m", "highrise", "main:AXIBot", "TU_ID_SALA", "TU_TOKEN_MAIN"])
p2 = subprocess.Popen(["python", "-m", "highrise", "dj:DJBot", "TU_ID_SALA", "TU_TOKEN_DJ"])

p1.wait()
p2.wait()
