import os
import json
from flask import Flask, render_template, request, send_from_directory, jsonify
from flask_socketio import SocketIO
from threading import Thread
from audio_interface import start_audio_stream, effects_state  # certifique-se que effects_state está definido lá
from effects import tuner

# Diretórios
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', 'frontend'))
TEMPLATES_DIR = os.path.join(FRONTEND_DIR, 'templates')

# Inicialização do Flask
app = Flask(__name__,
            template_folder=TEMPLATES_DIR,
            static_folder=FRONTEND_DIR)

# Inicialização do SocketIO
socketio = SocketIO(app)

# --- Rota principal ---
@app.route('/')
def index():
    return render_template('index.html')

# --- Arquivos estáticos ---
@app.route('/css/<path:filename>')
def serve_css(filename):
    return send_from_directory(os.path.join(FRONTEND_DIR, 'css'), filename)

@app.route('/js/<path:filename>')
def serve_js(filename):
    return send_from_directory(os.path.join(FRONTEND_DIR, 'js'), filename)

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    return send_from_directory(os.path.join(FRONTEND_DIR, 'assets'), filename)

# --- API para aplicar efeitos dinamicamente ---
@app.route('/apply-effect', methods=['POST'])
def apply_effect():
    try:
        data = request.json
        effect = data.get('effect')
        enabled = data.get('enabled')
        params = data.get('params', {})

        if effect not in effects_state:
            return jsonify({"status": "error", "message": f"Efeito '{effect}' não encontrado"}), 400

        # Atualiza estado
        effects_state[effect]['enabled'] = bool(enabled)
        if isinstance(params, dict):
            effects_state[effect]['params'].update(params)

        print(f"[INFO] Efeito atualizado: {effect} | enabled: {enabled} | params: {effects_state[effect]['params']}")
        return jsonify({"status": "ok", "effect": effect})

    except Exception as e:
        print(f"[ERRO] Falha ao aplicar efeito: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# --- Thread para iniciar o stream de áudio ---
def run_audio():
    try:
        start_audio_stream()
    except Exception as e:
        print(f"[ERRO] Erro na thread de áudio: {e}")

# --- Main ---
if __name__ == '__main__':
    print("Iniciando servidor e stream de áudio...")
    # Thread separada para não travar o Flask
    audio_thread = Thread(target=run_audio, daemon=True)
    audio_thread.start()

    # Iniciar servidor Flask + SocketIO
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
