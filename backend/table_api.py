import json
from flask import Blueprint, request, jsonify, session
from database import get_db

table_bp = Blueprint('table', __name__)

# ── GET /api/table ────────────────────────────────────────────────────────────
# Returns the full table JSON. Any authenticated user may call this.
@table_bp.route('/api/table', methods=['GET'])
def get_table():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated.'}), 401

    conn = get_db()
    try:
        row = conn.execute('SELECT data FROM table_config WHERE id = 1').fetchone()
        if not row:
            return jsonify({'error': 'Table not found.'}), 404
        return jsonify(json.loads(row['data']))
    finally:
        conn.close()

# ── POST /api/table/save ──────────────────────────────────────────────────────
# Saves the full table JSON. Admin only.
@table_bp.route('/api/table/save', methods=['POST'])
def save_table():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated.'}), 401
    if session.get('role') != 'admin':
        return jsonify({'error': 'Admin access required.'}), 403

    data = request.get_json()
    # Validate minimal structure
    if not isinstance(data.get('columns'), list) or not isinstance(data.get('rows'), list):
        return jsonify({'error': 'Invalid table structure.'}), 400

    conn = get_db()
    try:
        conn.execute(
            "UPDATE table_config SET data = ?, updated_at = datetime('now') WHERE id = 1",
            (json.dumps(data),)
        )
        if conn.execute('SELECT changes()').fetchone()[0] == 0:
            # Row doesn't exist yet — insert it
            conn.execute(
                "INSERT INTO table_config (id, data) VALUES (1, ?)",
                (json.dumps(data),)
            )
        conn.commit()
        return jsonify({'message': 'Table saved.'})
    finally:
        conn.close()
