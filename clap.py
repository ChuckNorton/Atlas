from flask import Flask, request
from flask_socketio import SocketIO, send
import subprocess
import datetime
import os

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")  # libera acesso externo

LOGS_DIR = "logs"
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOGS_DIR, "command_logs.txt")

def log_command(cmd, sid):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{now}] {sid} -> {cmd}\n")

@socketio.on("message")
def handle_message(msg):
    log_command(msg, request.sid)
    output = subprocess.getoutput(msg)
    send(output)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Render define a porta
    socketio.run(app, host="0.0.0.0", port=port)
