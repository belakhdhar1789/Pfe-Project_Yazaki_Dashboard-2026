"""Test: test_register_missing_fields - Authentication"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
import pytest, json
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c

def test_register_missing_fields(client):
    response = client.post('/api/auth/register',
        json={'full_name': 'John Doe', 'email': 'john@test.com'},
        content_type='application/json')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    print(f"✅ test_register_missing_fields PASSED")
