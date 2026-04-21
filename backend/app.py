import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, jsonify, send_from_directory
from flask_socketio import SocketIO
from database import init_db
from auth import auth_bp

app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')
app.config['SECRET_KEY'] = 'yazaki-secret-2026'

socketio = SocketIO(app, cors_allowed_origins="*")

app.register_blueprint(auth_bp)

@app.route('/')
def index():
    return send_from_directory('../frontend/templates', 'login.html')

@app.route('/api/health')
def health():
    return jsonify({"status": "ok"})

@app.route('/pending')
def pending():
    return send_from_directory('../frontend/templates', 'pending.html')

@app.route('/signup')
def signup():
    return send_from_directory('../frontend/templates', 'signup.html')

if __name__ == '__main__':
    init_db()
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)