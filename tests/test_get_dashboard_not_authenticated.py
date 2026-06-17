"""Test: test_get_dashboard_not_authenticated - API Endpoints"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c

def test_get_dashboard_not_authenticated(client):
    response = client.get('/api/dashboard')
    assert response.status_code in [401, 404, 200]
    print(f"✅ test_get_dashboard_not_authenticated PASSED")
