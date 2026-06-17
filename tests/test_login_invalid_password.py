"""Test: test_login_invalid_password - Authentication"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
import pytest, json
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c

def test_login_invalid_password(client):
    response = client.post('/api/auth/login', json={'email': 'admin@yazaki.com', 'password': 'wrongpassword'}, content_type='application/json')
    assert response.status_code in [401, 400]
    print(f"✅ test_login_invalid_password PASSED")
