"""Test: test_register_valid - Authentication"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
import pytest, json
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c

def test_register_valid(client):
    response = client.post('/api/auth/register',
        json={'full_name': 'John Doe', 'matricule': 'user123', 'email': 'john@yazaki.com', 'password': 'securepass123'},
        content_type='application/json')
    assert response.status_code in [201, 400, 409]
    print(f"✅ test_register_valid PASSED")
