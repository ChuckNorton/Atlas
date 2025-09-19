import os
import re
from flask import Flask, request, jsonify, send_from_directory, session, url_for
from datetime import datetime
import time
import subprocess
import sys

# =====================================================================
# ✅ INÍCIO DA SEÇÃO CORRIGIDA PARA EXECUÇÃO EM BACKGROUND
# =====================================================================
def run_external_script_background():
    """
    Executa o script 'clap.py' em um processo separado (background)
    e não espera por sua conclusão.
    """
    try:
        script_path = os.path.join(BASE_DIR, 'clap.py')
        if not os.path.exists(script_path):
            print(f"AVISO: O script '{script_path}' não foi encontrado e não será executado.")
            return

        print(f"--- Disparando script externo em background: {script_path} ---")

        # CORREÇÃO: Usando subprocess.Popen em vez de .run()
        # Popen inicia o processo e não espera por ele. O app continua imediatamente.
        # As saídas (stdout/stderr) são redirecionadas para DEVNULL para não travar o processo principal.
        subprocess.Popen(
            [sys.executable, script_path],
            stdout=subprocess.DEVNULL, # Descarta a saída padrão
            stderr=subprocess.DEVNULL  # Descarta a saída de erro
        )
        
        print("--- Script disparado. O servidor continuará a iniciar. ---")

    except FileNotFoundError:
        print(f"ERRO: O arquivo 'clap.py' não foi encontrado.")
    except Exception as e:
        print(f"Um erro inesperado ocorreu ao tentar disparar o script: {e}")

# =====================================================================
# ✅ FIM DA SEÇÃO CORRIGIDA
# =====================================================================


app = Flask(__name__, static_url_path='/static', static_folder='static')
app.secret_key = 'uma_chave_secreta_muito_segura_e_dificil_de_adivinhar'

# --- Configurações ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
LOGS_FOLDER = os.path.join(BASE_DIR, 'logs')

# --- Chamada da função no início ---
run_external_script_background()

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['LOGS_FOLDER'] = LOGS_FOLDER

# Garante que os diretórios de upload e logs existam
os.makedirs(os.path.join(UPLOAD_FOLDER, 'img'), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_FOLDER, 'txt'), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_FOLDER, 'arq'), exist_ok=True)
os.makedirs(LOGS_FOLDER, exist_ok=True)

# (O restante do seu código app.py continua aqui, sem alterações)
# ...
# ... Cole o resto do código do app.py aqui
# ...


# --- Funções Auxiliares (Lógica de Log igual ao PHP) ---

def count_log_lines(log_filename):
    """Conta as linhas de um arquivo de log."""
    log_path = os.path.join(app.config['LOGS_FOLDER'], log_filename)
    if not os.path.exists(log_path):
        return 0
    with open(log_path, 'r') as f:
        return len(f.readlines())

# --- Rotas da API (Corrigidas) ---

@app.route('/api/login', methods=['POST'])
def login():
    password = request.form.get('password')
    if password == 'Csgo8':
        session['logged_in'] = True
        return jsonify({'success': True})
    return jsonify({'success': False}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('logged_in', None)
    return jsonify({'success': True})

@app.route('/api/check_session')
def check_session():
    logged_in = 'logged_in' in session and session['logged_in']
    return jsonify({'loggedin': logged_in})

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'fileToUpload' not in request.files:
        return jsonify({'success': False, 'message': 'Nenhum arquivo enviado'}), 400
    file = request.files['fileToUpload']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'Nome de arquivo vazio'}), 400
    
    filename = os.path.basename(file.filename) # Segurança
    file_type = file.mimetype.split('/')[0]
    
    subdir = 'arq'
    if file_type == 'image':
        subdir = 'img'
    elif file_type == 'text':
        subdir = 'txt'

    save_path = os.path.join(app.config['UPLOAD_FOLDER'], subdir)
    file.save(os.path.join(save_path, filename))
    
    # Log no formato do PHP
    log_file = os.path.join(app.config['LOGS_FOLDER'], 'uploads.log')
    log_entry = f"{request.remote_addr}|{int(time.time())}|{request.user_agent.string}|{filename}\n"
    with open(log_file, 'a') as f:
        f.write(log_entry)

    return jsonify({'success': True, 'message': 'Arquivo enviado com sucesso!'})


@app.route('/api/files/<folder>')
def list_files(folder):
    if folder in ['img', 'txt'] and not session.get('logged_in'):
        return jsonify([]), 403

    folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder)
    if not os.path.isdir(folder_path):
        return jsonify([])

    files_data = []
    for f in os.listdir(folder_path):
        file_path = os.path.join(folder_path, f)
        if os.path.isfile(file_path):
            files_data.append({
                'name': f,
                'modified': int(os.path.getmtime(file_path))
            })
    return jsonify(files_data)


@app.route('/api/download/<category>/<filename>')
def download_file(category, filename):
    if category in ['img', 'txt'] and not session.get('logged_in'):
         return "Acesso negado", 403

    # Log no formato do PHP
    log_file = os.path.join(app.config['LOGS_FOLDER'], 'downloads.log')
    log_entry = f"{request.remote_addr}|{int(time.time())}|{request.user_agent.string}|{filename}\n"
    with open(log_file, 'a') as f:
        f.write(log_entry)

    directory = os.path.join(app.config['UPLOAD_FOLDER'], category)
    return send_from_directory(directory, filename, as_attachment=True)


@app.route('/api/tracker', methods=['POST'])
def tracker():
    log_file = os.path.join(app.config['LOGS_FOLDER'], 'visitors.log')
    ip = request.remote_addr
    today = datetime.now().strftime('%Y-%m-%d')
    is_unique_today = True

    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) >= 2 and parts[0] == ip:
                    log_date = datetime.fromtimestamp(int(parts[1])).strftime('%Y-%m-%d')
                    if log_date == today:
                        is_unique_today = False
                        break
    
    if is_unique_today:
        log_entry = f"{ip}|{int(time.time())}|{request.user_agent.string}\n"
        with open(log_file, 'a') as f:
            f.write(log_entry)

    return jsonify({'success': True})

@app.route('/api/counts')
def get_counts():
    counts = {
        "visitors": count_log_lines('visitors.log'),
        "downloads": count_log_lines('downloads.log'),
        "uploads": count_log_lines('uploads.log')
    }
    return jsonify(counts)

@app.route('/api/logs/<log_type>')
def get_logs(log_type):
    if not session.get('logged_in'):
        return jsonify({'error': 'Acesso Negado'}), 403
    
    log_map = { "visitors": "visitors.log", "downloads": "downloads.log", "uploads": "uploads.log" }
    log_filename = log_map.get(log_type)
    if not log_filename:
        return jsonify([])

    log_path = os.path.join(app.config['LOGS_FOLDER'], log_filename)
    if not os.path.exists(log_path):
        return jsonify([])

    log_data = []
    with open(log_path, 'r') as f:
        lines = reversed(f.readlines()) # Ler em ordem reversa como no PHP
        for line in lines:
            parts = line.strip().split('|')
            entry = {
                'ip': parts[0] if len(parts) > 0 else 'N/A',
                'datetime': datetime.fromtimestamp(int(parts[1])).strftime('%d/%m/%Y %H:%M:%S') if len(parts) > 1 else 'N/A',
                'device': parts[2] if len(parts) > 2 else 'N/A'
            }
            if log_type != 'visitors' and len(parts) > 3:
                entry['file'] = parts[3]
            log_data.append(entry)

    return jsonify(log_data)


@app.route('/api/file_info/<filename>')
def get_file_info(filename):
    if not session.get('logged_in'):
        return jsonify({'found': False}), 403
    
    log_path = os.path.join(app.config['LOGS_FOLDER'], 'uploads.log')
    if not os.path.exists(log_path):
        return jsonify({'found': False})

    with open(log_path, 'r') as f:
        for line in reversed(f.readlines()):
            parts = line.strip().split('|')
            if len(parts) >= 4 and parts[3] == filename:
                return jsonify({
                    'found': True,
                    'ip': parts[0],
                    'datetime': datetime.fromtimestamp(int(parts[1])).strftime('%d/%m/%Y %H:%M:%S'),
                    'device': parts[2]
                })

    return jsonify({'found': False})


# --- Rotas para servir arquivos estáticos e o frontend ---

@app.route('/')
def index():
    return send_from_directory('templates', 'index.html')

@app.route('/<path:folder>/<path:filename>')
def serve_static_files(folder, filename):
    # Rota para servir CSS, JS, fontes, etc.
    return send_from_directory(os.path.join(BASE_DIR, folder), filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)