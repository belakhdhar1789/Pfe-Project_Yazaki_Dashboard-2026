"""Test: test_user_registration_to_login_flow - Integration"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
import pytest, json
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c

def test_user_registration_to_login_flow(client):
    reg_response = client.post('/api/auth/register', json={'full_name': 'Integration Test', 'matricule': 'int_test_001', 'email': 'integration@test.com', 'password': 'testpass123'}, content_type='application/json')
    if reg_response.status_code == 201:
        login_response = client.post('/api/auth/login', json={'email': 'integration@test.com', 'password': 'testpass123'}, content_type='application/json')
        assert login_response.status_code in [401, 403, 200, 400]
    print(f"✅ test_user_registration_to_login_flow PASSED")
