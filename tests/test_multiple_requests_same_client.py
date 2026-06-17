"""Test: test_multiple_requests_same_client - Performance"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c

def test_multiple_requests_same_client(client):
    for i in range(5):
        response = client.post('/api/auth/login', json={'email': 'admin@yazaki.com', 'password': 'wrong'}, content_type='application/json')
        assert response.status_code in [401, 400, 429]
    print(f"✅ test_multiple_requests_same_client PASSED")
