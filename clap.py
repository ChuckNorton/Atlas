from flask import Flask, request
from flask_sock import Sock
import subprocess
import datetime
import os

app = Flask(__name__)
sock = Sock(app)

LOGS_DIR = "logs"
os.makedirs(LOGS_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOGS_DIR, "command_logs.txt")

def log_command(cmd, peer):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{now}] {peer} -> {cmd}\n")

# rota websocket em /ws
@sock.route("/ws")
def ws(ws):
    peer = ws.environ.get("REMOTE_ADDR", "unknown")
    ws.send("WebSocket shell iniciado!\n")
    for msg in ws:
        # msg é texto (string)
        log_command(msg, peer)
        output = subprocess.getoutput(msg)
        # envie saída de volta
        ws.send(output)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    # Render recomenda rodar host 0.0.0.0
    app.run(host="0.0.0.0", port=port)
