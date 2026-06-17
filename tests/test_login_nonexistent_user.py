"""Test: test_login_nonexistent_user - Authentication"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
import pytest, json
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c

def test_login_nonexistent_user(client):
    response = client.post('/api/auth/login', json={'email': 'nonexistent@yazaki.com', 'password': 'anypassword'}, content_type='application/json')
    assert response.status_code in [401, 400]
    print(f"✅ test_login_nonexistent_user PASSED")
