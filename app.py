import os
import re
from flask import Flask, request, jsonify, send_from_directory, session, url_for
from datetime import datetime
import time
import subprocess
import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
# ✅ 1. IMPORTAÇÃO ADICIONADA
from werkzeug.middleware.proxy_fix import ProxyFix

# =====================================================================
# SEÇÃO DE EXECUÇÃO EM BACKGROUND
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
        subprocess.Popen(
            [sys.executable, script_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print("--- Script disparado. O servidor continuará a iniciar. ---")
    except Exception as e:
        print(f"Um erro inesperado ocorreu ao tentar disparar o script: {e}")

# =====================================================================
# CONFIGURAÇÃO DO APP FLASK
# =====================================================================
app = Flask(__name__, static_url_path='/static', static_folder='static')

# ✅ 2. APLICAÇÃO DO MIDDLEWARE PROXYFIX
# Esta linha corrige o problema do IP. Ela instrui o Flask a confiar
# no cabeçalho enviado pelo proxy reverso para obter o IP real do visitante.
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)


app.secret_key = 'uma_chave_secreta_muito_segura_e_dificil_de_adivinhar'
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
LOGS_FOLDER = os.path.join(BASE_DIR, 'logs')

# --- Chamada da função no início ---
run_external_script_background()

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['LOGS_FOLDER'] = LOGS_FOLDER

os.makedirs(os.path.join(UPLOAD_FOLDER, 'img'), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_FOLDER, 'txt'), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_FOLDER, 'arq'), exist_ok=True)
os.makedirs(LOGS_FOLDER, exist_ok=True)

# --- Funções Auxiliares ---
def count_log_lines(log_filename):
    log_path = os.path.join(app.config['LOGS_FOLDER'], log_filename)
    if not os.path.exists(log_path):
        return 0
    with open(log_path, 'r', encoding='utf-8') as f:
        return len(f.readlines())

# --- Rotas da API ---

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
    
    filename = os.path.basename(file.filename)
    file_type = file.mimetype.split('/')[0]
    
    subdir = 'arq'
    if file_type == 'image':
        subdir = 'img'
    elif file_type == 'text':
        subdir = 'txt'

    save_path = os.path.join(app.config['UPLOAD_FOLDER'], subdir)
    file.save(os.path.join(save_path, filename))
    
    log_file = os.path.join(app.config['LOGS_FOLDER'], 'uploads.log')
    # Nenhuma mudança necessária aqui, request.remote_addr agora terá o IP correto
    log_entry = f"{request.remote_addr}|{int(time.time())}|{request.user_agent.string}|{filename}\n"
    with open(log_file, 'a', encoding='utf-8') as f:
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
def download_file_route(category, filename):
    if category in ['img', 'txt'] and not session.get('logged_in'):
        return "Acesso negado", 403

    log_file = os.path.join(app.config['LOGS_FOLDER'], 'downloads.log')
    # Nenhuma mudança necessária aqui
    log_entry = f"{request.remote_addr}|{int(time.time())}|{request.user_agent.string}|{filename}\n"
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(log_entry)

    directory = os.path.join(app.config['UPLOAD_FOLDER'], category)
    return send_from_directory(directory, filename, as_attachment=True)


@app.route('/api/tracker', methods=['POST'])
def tracker():
    log_file = os.path.join(app.config['LOGS_FOLDER'], 'visitors.log')
    # Nenhuma mudança necessária aqui
    ip = request.remote_addr
    today = datetime.now().strftime('%Y-%m-%d')
    is_unique_today = True

    if os.path.exists(log_file):
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) >= 2 and parts[0] == ip:
                    log_date = datetime.fromtimestamp(int(parts[1])).strftime('%Y-%m-%d')
                    if log_date == today:
                        is_unique_today = False
                        break
    
    if is_unique_today:
        log_entry = f"{ip}|{int(time.time())}|{request.user_agent.string}\n"
        with open(log_file, 'a', encoding='utf-8') as f:
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
    with open(log_path, 'r', encoding='utf-8') as f:
        lines = reversed(f.readlines())
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

    with open(log_path, 'r', encoding='utf-8') as f:
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


# --- ROTA PARA WEB SCRAPING ---

def get_best_image_from_srcset(srcset):
    if not srcset: return None
    try:
        sources = [s.strip().split(' ') for s in srcset.split(',')]
        sized_sources = [s for s in sources if len(s) == 2 and s[1].endswith('w')]
        if not sized_sources: return sources[0][0]
        best_source = max(sized_sources, key=lambda s: int(s[1][:-1]))
        return best_source[0]
    except Exception: return None

@app.route('/api/scrape_article')
def scrape_article():
    article_url = request.args.get('url')
    if not article_url:
        return jsonify({'error': 'Parâmetro "url" é obrigatório'}), 400
    
    base_url = "https://hellenicmoon.com"
    headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36' }

    try:
        response = requests.get(article_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # --- Extração de dados (sem alterações) ---
        title_tag = soup.select_one('h1.entry-title, h1')
        title = title_tag.get_text(strip=True) if title_tag else 'Título não encontrado'

        category_tag = soup.select_one('span.category a, .cat-links a')
        category = category_tag.get_text(strip=True) if category_tag else 'Sem Categoria'

        summary_tag = soup.select_one('div.entry-content p, div.td-post-content p')
        summary = summary_tag.get_text(strip=True) if summary_tag else ''

        image_url = ''
        image_tag = soup.select_one('img.wp-post-image')
        if not image_tag:
            content_area = soup.select_one('div.entry-content, div.td-post-content')
            if content_area: image_tag = content_area.select_one('img')
        if image_tag:
            if image_tag.get('data-srcset'): image_url = get_best_image_from_srcset(image_tag.get('data-srcset'))
            elif image_tag.get('data-src'): image_url = image_tag.get('data-src')
            elif image_tag.get('srcset'): image_url = get_best_image_from_srcset(image_tag.get('srcset'))
            else: image_url = image_tag.get('src', '')
        if not image_url or 'data:image/svg+xml' in image_url:
            og_image_tag = soup.select_one('meta[property="og:image"]')
            if og_image_tag: image_url = og_image_tag.get('content', '')
        if image_url and image_url.startswith('/'):
            image_url = urljoin(base_url, image_url)
        
        full_content_html = ''
        content_tag = soup.select_one('div.entry-content, div.td-post-content')
        
        if content_tag:
            media_tags = content_tag.find_all(['img', 'iframe'])
            for tag in media_tags:
                for attr in ['src', 'srcset', 'data-src', 'data-srcset']:
                    if tag.has_attr(attr):
                        if tag[attr].strip().startswith('/'):
                            tag[attr] = urljoin(base_url, tag[attr])
            
            full_content_html = str(content_tag)
            
            cutoff_phrase = "Subscribe to get the latest posts sent to your email."
            cutoff_index = full_content_html.find(cutoff_phrase)
            
            if cutoff_index != -1:
                full_content_html = full_content_html[:cutoff_index]
        else:
            full_content_html = '<p>Conteúdo completo não encontrado.</p>'

        data = {
            'title': title, 'category': category, 'summary': summary, 'imageUrl': image_url,
            'full_content_html': full_content_html
        }
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': f'Ocorreu um erro durante o scraping: {e}'}), 500

# --- ROTAS PARA SERVIR ARQUIVOS ---

@app.route('/')
def index():
    return send_from_directory('templates', 'index.html')

@app.route('/<path:folder>/<path:filename>')
def serve_static_files(folder, filename):
    return send_from_directory(os.path.join(BASE_DIR, folder), filename)

if __name__ == '__main__':
    # Em desenvolvimento local, o app.run não usa o ProxyFix, o que é o comportamento esperado.
    # Em produção, um servidor WSGI (como Gunicorn) usará o objeto 'app', que já está "envelopado" pelo ProxyFix.
    app.run(debug=True, host='0.0.0.0', port=5000)