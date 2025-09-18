import socket
import subprocess
import threading
import datetime
import os

# Bind na Render
HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", 10000))  # usa a porta do Render ou 10000 como fallback

LOGS_DIR = "logs"
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOGS_DIR, "command_logs.txt")

# Função para registrar comandos
def log_command(cmd, user_ip):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{now}] {user_ip} -> {cmd}\n")

# Função que trata cada cliente
def handle_client(conn, addr):
    user_ip = addr[0]
    conn.send(b"Bind shell Python Render iniciado!\n")
    while True:
        try:
            conn.send(b"$ ")
            cmd = conn.recv(1024).decode().strip()
            if not cmd:
                continue
            if cmd.lower() in ("exit", "quit"):
                break
            log_command(cmd, user_ip)
            output = subprocess.getoutput(cmd)
            conn.send(output.encode() + b"\n")
        except Exception as e:
            conn.send(f"Erro: {e}\n".encode())
            break
    conn.close()
    print(f"[-] Conexão de {user_ip} encerrada.")

# Servidor principal
def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(5)
    print(f"[+] Bind shell rodando em {HOST}:{PORT}")
    
    while True:
        conn, addr = s.accept()
        print(f"[+] Nova conexão de {addr}")
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    # Cria arquivo de log se não existir
    if not os.path.exists(LOG_FILE):
        open(LOG_FILE, "w").close()
    main()
