import json
from flask import Blueprint, request, jsonify, session
from database import get_db

dc_bp = Blueprint('data_collection', __name__)

# ── GET /api/data-collection ──────────────────────────────────────────────────
# Returns the full data collection JSON. Any authenticated user may call this.
@dc_bp.route('/api/data-collection', methods=['GET'])
def get_dc_data():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated.'}), 401

    conn = get_db()
    try:
        row = conn.execute(
            'SELECT data FROM data_collection_config WHERE id = 1'
        ).fetchone()
        if not row:
            return jsonify({'error': 'Data not found.'}), 404
        return jsonify(json.loads(row['data']))
    finally:
        conn.close()

# ── POST /api/data-collection/save ───────────────────────────────────────────
# Saves the full data collection JSON. Admin only.
@dc_bp.route('/api/data-collection/save', methods=['POST'])
def save_dc_data():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated.'}), 401
    if session.get('role') != 'admin':
        return jsonify({'error': 'Admin access required.'}), 403

    data = request.get_json(silent=True)
    if not data or not isinstance(data.get('rows'), list):
        return jsonify({'error': 'Invalid data structure.'}), 400

    conn = get_db()
    try:
        conn.execute(
            "UPDATE data_collection_config SET data = ?, updated_at = datetime('now') WHERE id = 1",
            (json.dumps(data),)
        )
        if conn.execute('SELECT changes()').fetchone()[0] == 0:
            conn.execute(
                "INSERT INTO data_collection_config (id, data) VALUES (1, ?)",
                (json.dumps(data),)
            )
        conn.commit()
        return jsonify({'message': 'Data collection saved.'})
    finally:
        conn.close()
