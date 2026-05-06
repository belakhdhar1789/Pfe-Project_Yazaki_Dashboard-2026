import json
from flask import Blueprint, request, jsonify, session
from database import get_db

cables_bp = Blueprint('cables', __name__)

# ── GET /api/cables/plots ─────────────────────────────────────────────────────
@cables_bp.route('/api/cables/plots', methods=['GET'])
def get_plots():
    if not session.get('user_id'):
        return jsonify({'error': 'Not authenticated.'}), 401
    conn = get_db()
    try:
        rows = conn.execute('SELECT * FROM plots ORDER BY id').fetchall()
        return jsonify([dict(r) for r in rows])
    finally:
        conn.close()

# ── PUT /api/cables/plots/<id> ────────────────────────────────────────────────
# Admin sets expected cable type (and optionally line/WS name) for a plot.
@cables_bp.route('/api/cables/plots/<int:plot_id>', methods=['PUT'])
def update_plot(plot_id):
    if session.get('role') != 'admin':
        return jsonify({'error': 'Admin only.'}), 403
    data = request.get_json(silent=True) or {}
    allowed = ('expected_cable_type', 'line_name', 'workstation_name', 'plot_number')
    fields, values = [], []
    for col in allowed:
        if col in data:
            fields.append(f"{col} = ?")
            values.append(data[col])
    if not fields:
        return jsonify({'error': 'Nothing to update.'}), 400
    values.append(plot_id)
    conn = get_db()
    try:
        conn.execute(
            f"UPDATE plots SET {', '.join(fields)}, updated_at = datetime('now') WHERE id = ?",
            values
        )
        conn.commit()
        return jsonify({'message': 'Plot updated.'})
    finally:
        conn.close()

# ── POST /api/cables/scan ─────────────────────────────────────────────────────
# Called by camera (admin) OR by ESP/MQTT bridge.
# Body: { plot_id: int, cable_type: str, source: "camera"|"esp"|"mqtt" }
@cables_bp.route('/api/cables/scan', methods=['POST'])
def scan_cable():
    if not session.get('user_id'):
        return jsonify({'error': 'Not authenticated.'}), 401
    data = request.get_json(silent=True) or {}
    plot_id    = data.get('plot_id')
    cable_type = (data.get('cable_type') or '').strip()
    source     = data.get('source', 'camera')

    if not plot_id or not cable_type:
        return jsonify({'error': 'plot_id and cable_type are required.'}), 400

    conn = get_db()
    try:
        plot = conn.execute('SELECT * FROM plots WHERE id = ?', (plot_id,)).fetchone()
        if not plot:
            return jsonify({'error': 'Plot not found.'}), 404

        expected = (plot['expected_cable_type'] or '').strip()
        result   = 'ok' if (expected and cable_type == expected) else 'wrong_type'
        if not expected:
            result = 'no_expected'

        conn.execute(
            "UPDATE plots SET current_cable_type = ?, last_scan_at = datetime('now'), "
            "ir_status = CASE WHEN ir_status = 'refilled' THEN 'ok' ELSE ir_status END, "
            "updated_at = datetime('now') WHERE id = ?",
            (cable_type, plot_id)
        )
        conn.execute(
            "INSERT INTO scan_log (plot_id, cable_type, source, result) VALUES (?, ?, ?, ?)",
            (plot_id, cable_type, source, result)
        )
        conn.commit()

        if result == 'ok':
            alert = f'✅ Correct cable type: {cable_type}'
        elif result == 'wrong_type':
            alert = f'⚠ WRONG TYPE — Expected: {expected} | Got: {cable_type}'
        else:
            alert = f'ℹ No expected type configured for this plot. Scanned: {cable_type}'

        return jsonify({
            'result':   result,
            'alert':    alert,
            'expected': expected,
            'scanned':  cable_type,
            'plot':     dict(plot)
        })
    finally:
        conn.close()

# ── POST /api/cables/ir ───────────────────────────────────────────────────────
# Called by ESP/IR sensor bridge OR manually for testing.
# Body: { plot_id: int, event: "low"|"refilled"|"empty", source: "sensor"|"manual" }
@cables_bp.route('/api/cables/ir', methods=['POST'])
def ir_event():
    data   = request.get_json(silent=True) or {}
    plot_id = data.get('plot_id')
    event   = (data.get('event') or '').strip()
    source  = data.get('source', 'sensor')

    if not plot_id or event not in ('low', 'refilled', 'empty'):
        return jsonify({'error': 'plot_id and event (low/refilled/empty) required.'}), 400

    conn = get_db()
    try:
        low_since = ''
        if event == 'low':
            import datetime
            low_since = datetime.datetime.utcnow().isoformat()

        conn.execute(
            "UPDATE plots SET ir_status = ?, low_since = ?, updated_at = datetime('now') WHERE id = ?",
            (event, low_since, plot_id)
        )
        conn.execute(
            "INSERT INTO ir_log (plot_id, event, source) VALUES (?, ?, ?)",
            (plot_id, event, source)
        )
        conn.commit()
        return jsonify({'message': f'IR event "{event}" recorded for plot {plot_id}.'})
    finally:
        conn.close()

# ── GET /api/cables/scan-log ──────────────────────────────────────────────────
@cables_bp.route('/api/cables/scan-log', methods=['GET'])
def get_scan_log():
    if not session.get('user_id'):
        return jsonify({'error': 'Not authenticated.'}), 401
    conn = get_db()
    try:
        rows = conn.execute('''
            SELECT s.id, s.cable_type, s.source, s.result, s.scanned_at,
                   p.workstation_name, p.plot_number, p.line_name
            FROM scan_log s
            JOIN plots p ON s.plot_id = p.id
            ORDER BY s.scanned_at DESC
            LIMIT 30
        ''').fetchall()
        return jsonify([dict(r) for r in rows])
    finally:
        conn.close()
