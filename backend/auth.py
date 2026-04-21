from flask import Blueprint, request, jsonify, session
from database import get_connection, hash_password

auth_bp = Blueprint('auth', __name__)

PAGES = ['dashboard', 'handbook', 'data_collection', 'batch_ksk', 'home']

# ─── REGISTER ───────────────────────────────────────────────
@auth_bp.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    full_name = data.get('full_name', '').strip()
    matricule = data.get('matricule', '').strip()
    email     = data.get('email', '').strip()
    password  = data.get('password', '').strip()

    if not full_name or not matricule or not email or not password:
        return jsonify({"error": "All fields are required"}), 400

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE matricule = ?", (matricule,))
    if cursor.fetchone():
        conn.close()
        return jsonify({"error": "Matricule already registered"}), 409

    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    if cursor.fetchone():
        conn.close()
        return jsonify({"error": "Email already registered"}), 409

    cursor.execute(
        "INSERT INTO users (full_name, matricule, email, password, role, status) VALUES (?, ?, ?, ?, ?, ?)",
        (full_name, matricule, email, hash_password(password), 'user', 'pending')
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Request submitted. Waiting for admin approval."}), 201


# ─── LOGIN ───────────────────────────────────────────────────
@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email    = data.get('email', '').strip()
    password = data.get('password', '').strip()

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        return jsonify({"error": "Invalid email or password"}), 401

    if user['password'] != hash_password(password):
        return jsonify({"error": "Invalid email or password"}), 401

    if user['status'] == 'pending':
        return jsonify({"error": "Your account is pending approval."}), 403

    if user['status'] == 'blocked':
        return jsonify({"error": "Your account has been blocked. Contact admin."}), 403

    session['user_id']   = user['id']
    session['role']      = user['role']
    session['matricule'] = user['matricule']
    session['full_name'] = user['full_name']

    return jsonify({
        "message": "Login successful",
        "role": user['role'],
        "full_name": user['full_name'],
        "redirect": "/admin" if user['role'] == 'admin' else "/home"
    }), 200


# ─── LOGOUT ──────────────────────────────────────────────────
@auth_bp.route('/api/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"message": "Logged out"}), 200


# ─── ADMIN — LIST USERS ──────────────────────────────────────
@auth_bp.route('/api/admin/users', methods=['GET'])
def get_users():
    if session.get('role') != 'admin':
        return jsonify({"error": "Unauthorized"}), 403

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, full_name, matricule, role, status, created_at FROM users WHERE role != 'admin'")
    users = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(users), 200


# ─── ADMIN — APPROVE USER ────────────────────────────────────
@auth_bp.route('/api/admin/users/<int:user_id>/approve', methods=['PUT'])
def approve_user(user_id):
    if session.get('role') != 'admin':
        return jsonify({"error": "Unauthorized"}), 403

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET status = 'active' WHERE id = ?", (user_id,))

    for page in PAGES:
        cursor.execute(
            "INSERT OR IGNORE INTO permissions (user_id, page_name, can_access) VALUES (?, ?, 1)",
            (user_id, page)
        )
    conn.commit()
    conn.close()
    return jsonify({"message": "User approved"}), 200


# ─── ADMIN — BLOCK USER ──────────────────────────────────────
@auth_bp.route('/api/admin/users/<int:user_id>/block', methods=['PUT'])
def block_user(user_id):
    if session.get('role') != 'admin':
        return jsonify({"error": "Unauthorized"}), 403

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET status = 'blocked' WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "User blocked"}), 200


# ─── ADMIN — DELETE USER ─────────────────────────────────────
@auth_bp.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    if session.get('role') != 'admin':
        return jsonify({"error": "Unauthorized"}), 403

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM permissions WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "User deleted"}), 200


# ─── ADMIN — UPDATE PERMISSIONS ──────────────────────────────
@auth_bp.route('/api/admin/permissions', methods=['PUT'])
def update_permissions():
    if session.get('role') != 'admin':
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    user_id    = data.get('user_id')
    page_name  = data.get('page_name')
    can_access = 1 if data.get('can_access') else 0

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO permissions (user_id, page_name, can_access) VALUES (?, ?, ?)",
        (user_id, page_name, can_access)
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Permission updated"}), 200


# ─── CHECK SESSION ────────────────────────────────────────────
@auth_bp.route('/api/auth/me', methods=['GET'])
def me():
    if 'user_id' not in session:
        return jsonify({"error": "Not logged in"}), 401
    return jsonify({
        "user_id": session['user_id'],
        "role": session['role'],
        "full_name": session['full_name'],
        "matricule": session['matricule']
    }), 200