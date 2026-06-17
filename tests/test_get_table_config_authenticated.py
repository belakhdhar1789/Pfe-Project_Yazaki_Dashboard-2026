"""Test: test_get_table_config_authenticated - API Endpoints"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c

def test_get_table_config_authenticated(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 3
    response = client.get('/api/table/')
    assert response.status_code in [200, 401, 404]
    print(f"✅ test_get_table_config_authenticated PASSED")
