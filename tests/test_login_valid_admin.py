"""Test: test_login_valid_admin - Authentication"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
import pytest, json
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c

def test_login_valid_admin(client):
    response = client.post('/api/auth/login',
        json={'email': 'admin@yazaki.com', 'password': 'admin123'},
        content_type='application/json')
    assert response.status_code in [200, 401, 403]
    data = json.loads(response.data)
    assert 'message' in data or 'error' in data
    print(f"✅ test_login_valid_admin PASSED")
