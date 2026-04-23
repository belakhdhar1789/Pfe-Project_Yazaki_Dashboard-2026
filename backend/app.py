import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, jsonify, send_from_directory, session
from flask_socketio import SocketIO
from database import init_db
from auth import auth_bp 
from table_api import table_bp
app.register_blueprint(table_bp)

app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')
app.config['SECRET_KEY'] = 'yazaki-secret-2026'

socketio = SocketIO(app, cors_allowed_origins="*")
app.register_blueprint(auth_bp)

TEMPLATES = '../frontend/templates'

@app.route('/')
def index():
    return send_from_directory(TEMPLATES, 'login.html')

@app.route('/signup')
def signup():
    return send_from_directory(TEMPLATES, 'signup.html')

@app.route('/pending')
def pending():
    return send_from_directory(TEMPLATES, 'pending.html')

@app.route('/handbook')
def handbook():
    return send_from_directory(TEMPLATES, 'handbook.html')

@app.route('/dashboard')
def dashboard():
    return send_from_directory(TEMPLATES, 'dashboard.html')

@app.route('/data-collection')
def data_collection():
    return send_from_directory(TEMPLATES, 'data_collection.html')

@app.route('/overview-batch')
def overview_batch():
    return send_from_directory(TEMPLATES, 'batch_ksk.html')

@app.route('/table')
def table():
    return send_from_directory(TEMPLATES, 'table.html')

@app.route('/revision-history')
def revision_history():
    return send_from_directory(TEMPLATES, 'revision_history.html')

@app.route('/profile')
def profile():
    return send_from_directory(TEMPLATES, 'profile.html')

@app.route('/admin')
def admin():
    return send_from_directory(TEMPLATES, 'admin.html')

@app.route('/api/health')
def health():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    init_db()
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)