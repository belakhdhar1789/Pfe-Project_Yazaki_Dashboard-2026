from flask import Flask, jsonify
from flask_socketio import SocketIO
from database import init_db

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yazaki-secret-2026'
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    return jsonify({"status": "ok", "message": "Yazaki Dashboard API running"})

@app.route('/api/health')
def health():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    init_db()
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)