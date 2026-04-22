from flask import Blueprint, request, jsonify, session
from database import get_db, hash_password
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

VALID_PAGES = ['handbook', 'dashboard', 'dataCollection', 'overviewBatch', 'table', 'revisionHistory']

def now_str():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# ── Register ──────────────────────────────────────────────────────────────────
@auth_bp.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    full_name  = (data.get('full_name') or '').strip()
    matricule  = (data.get('matricule') or '').strip()
    email      = (data.get('email') or '').strip().lower()
    password   = data.get('password') or ''

    if not all([full_name, matricule, email, password]):
        return jsonify({'error': 'All fields are required.'}), 400

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO users (full_name, matricule, email, password, role, status)
            VALUES (?, ?, ?, ?, 'user', 'pending')
        ''', (full_name, matricule, email, hash_password(password)))
        user_id = cursor.lastrowid
        # Create default permissions (all off)
        for page in VALID_PAGES:
            cursor.execute(
                'INSERT INTO permissions (user_id, page_name, can_access) VALUES (?, ?, 0)',
                (user_id, page)
            )
        conn.commit()
        return jsonify({'message': 'Registration successful. Awaiting admin approval.'}), 201
    except Exception as e:
        conn.rollback()
        msg = str(e)
        if 'UNIQUE' in msg and 'email' in msg:
            return jsonify({'error': 'Email already registered.'}), 409
        if 'UNIQUE' in msg and 'matricule' in msg:
            return jsonify({'error': 'Matricule already registered.'}), 409
        return jsonify({'error': 'Registration failed: ' + msg}), 500
    finally:
        conn.close()

# ── Login ─────────────────────────────────────────────────────────────────────
@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    data     = request.get_json()
    email    = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    if not email or not password:
        return jsonify({'error': 'Email and password are required.'}), 400

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'SELECT * FROM users WHERE email = ? AND password = ?',
            (email, hash_password(password))
        )
        user = cursor.fetchone()
        if not user:
            return jsonify({'error': 'Invalid email or password.'}), 401

        if user['status'] == 'pending':
            return jsonify({'error': 'Your account is pending admin approval.'}), 403
        if user['status'] == 'blocked':
            return jsonify({'error': 'Your account has been blocked. Contact admin.'}), 403

        # Update last_login timestamp
        cursor.execute(
            "UPDATE users SET last_login = ?, last_activity = ? WHERE id = ?",
            (now_str(), now_str(), user['id'])
        )
        conn.commit()

        # Store session
        session['user_id'] = user['id']
        session['role']    = user['role']

        redirect_url = '/admin' if user['role'] == 'admin' else '/handbook'
        return jsonify({
            'message':  'Login successful.',
            'redirect': redirect_url,
            'role':     user['role']
        })
    finally:
        conn.close()

# ── Logout ────────────────────────────────────────────────────────────────────
@auth_bp.route('/api/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out.'})

# ── Session check (me) ────────────────────────────────────────────────────────
@auth_bp.route('/api/auth/me', methods=['GET'])
def me():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated.'}), 401

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'SELECT id, full_name, matricule, email, role, status FROM users WHERE id = ?',
            (user_id,)
        )
        user = cursor.fetchone()
        if not user:
            session.clear()
            return jsonify({'error': 'User not found.'}), 401

        if user['status'] in ('pending', 'blocked'):
            session.clear()
            return jsonify({'error': 'Access denied.'}), 403

        return jsonify(dict(user))
    finally:
        conn.close()

# ── Update activity timestamp ─────────────────────────────────────────────────
@auth_bp.route('/api/auth/activity', methods=['POST'])
def update_activity():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated.'}), 401
    conn = get_db()
    try:
        conn.execute(
            "UPDATE users SET last_activity = ? WHERE id = ?",
            (now_str(), user_id)
        )
        conn.commit()
        return jsonify({'ok': True})
    finally:
        conn.close()

# ── Update email ──────────────────────────────────────────────────────────────
@auth_bp.route('/api/auth/update-email', methods=['POST'])
def update_email():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated.'}), 401

    data  = request.get_json()
    email = (data.get('email') or '').strip().lower()
    if not email:
        return jsonify({'error': 'Email is required.'}), 400

    conn = get_db()
    try:
        conn.execute('UPDATE users SET email = ? WHERE id = ?', (email, user_id))
        conn.commit()
        return jsonify({'message': 'Email updated successfully.'})
    except Exception as e:
        if 'UNIQUE' in str(e):
            return jsonify({'error': 'Email already in use.'}), 409
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

# ──────────────────────────────────────────────────────────────────────────────
#  ADMIN-ONLY ENDPOINTS
# ──────────────────────────────────────────────────────────────────────────────

def require_admin():
    """Returns None if OK, or (json_response, status_code) if not admin."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated.'}), 401
    role = session.get('role')
    if role != 'admin':
        return jsonify({'error': 'Admin access required.'}), 403
    return None

# ── Get all users (admin) ─────────────────────────────────────────────────────
@auth_bp.route('/api/auth/get_users', methods=['GET'])
def get_users():
    err = require_admin()
    if err: return err

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT id, full_name, matricule, email, role, status,
                   access_mode, last_login, last_activity, created_at
            FROM users
            WHERE role != 'admin'
            ORDER BY created_at DESC
        ''')
        rows = cursor.fetchall()
        users = []
        for row in rows:
            u = dict(row)
            cursor.execute(
                "SELECT page_name FROM permissions WHERE user_id = ? AND can_access = 1",
                (u['id'],)
            )
            u['permissions'] = [r['page_name'] for r in cursor.fetchall()]
            users.append(u)
        return jsonify(users)
    finally:
        conn.close()

# ── Approve user ──────────────────────────────────────────────────────────────
@auth_bp.route('/api/auth/approve', methods=['POST'])
def approve_user():
    err = require_admin()
    if err: return err

    user_id = request.get_json().get('user_id')
    conn = get_db()
    try:
        conn.execute("UPDATE users SET status = 'active' WHERE id = ?", (user_id,))
        conn.commit()
        return jsonify({'message': 'User approved.'})
    finally:
        conn.close()

# ── Block user ────────────────────────────────────────────────────────────────
@auth_bp.route('/api/auth/block', methods=['POST'])
def block_user():
    err = require_admin()
    if err: return err

    user_id = request.get_json().get('user_id')
    conn = get_db()
    try:
        conn.execute("UPDATE users SET status = 'blocked' WHERE id = ?", (user_id,))
        conn.commit()
        return jsonify({'message': 'User blocked.'})
    finally:
        conn.close()

# ── Unblock user ──────────────────────────────────────────────────────────────
@auth_bp.route('/api/auth/unblock', methods=['POST'])
def unblock_user():
    err = require_admin()
    if err: return err

    user_id = request.get_json().get('user_id')
    conn = get_db()
    try:
        conn.execute("UPDATE users SET status = 'active' WHERE id = ?", (user_id,))
        conn.commit()
        return jsonify({'message': 'User unblocked.'})
    finally:
        conn.close()

# ── Delete user ───────────────────────────────────────────────────────────────
@auth_bp.route('/api/auth/delete', methods=['DELETE'])
def delete_user():
    err = require_admin()
    if err: return err

    user_id = request.get_json().get('user_id')
    conn = get_db()
    try:
        conn.execute("DELETE FROM permissions WHERE user_id = ?", (user_id,))
        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        return jsonify({'message': 'User deleted.'})
    finally:
        conn.close()

# ── Update permissions ────────────────────────────────────────────────────────
@auth_bp.route('/api/auth/update_permissions', methods=['POST'])
def update_permissions():
    err = require_admin()
    if err: return err

    data        = request.get_json()
    user_id     = data.get('user_id')
    permissions = data.get('permissions', [])   # list of page_name strings

    conn = get_db()
    cursor = conn.cursor()
    try:
        for page in VALID_PAGES:
            can = 1 if page in permissions else 0
            cursor.execute(
                "SELECT id FROM permissions WHERE user_id = ? AND page_name = ?",
                (user_id, page)
            )
            if cursor.fetchone():
                cursor.execute(
                    "UPDATE permissions SET can_access = ? WHERE user_id = ? AND page_name = ?",
                    (can, user_id, page)
                )
            else:
                cursor.execute(
                    "INSERT INTO permissions (user_id, page_name, can_access) VALUES (?, ?, ?)",
                    (user_id, page, can)
                )
        conn.commit()
        return jsonify({'message': 'Permissions updated.'})
    finally:
        conn.close()

# ── Update access mode ────────────────────────────────────────────────────────
@auth_bp.route('/api/auth/update_access_mode', methods=['POST'])
def update_access_mode():
    err = require_admin()
    if err: return err

    data    = request.get_json()
    user_id = data.get('user_id')
    mode    = data.get('access_mode', 'manual')

    if mode not in ('manual', 'auto'):
        return jsonify({'error': 'Invalid access mode.'}), 400

    conn = get_db()
    try:
        conn.execute("UPDATE users SET access_mode = ? WHERE id = ?", (mode, user_id))
        conn.commit()
        return jsonify({'message': 'Access mode updated.'})
    finally:
        conn.close()
