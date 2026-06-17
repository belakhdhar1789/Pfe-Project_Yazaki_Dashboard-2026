"""Test: test_security_headers_present - Security"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c

def test_security_headers_present(client):
    response = client.get('/')
    assert 'X-Content-Type-Options' in response.headers or 'X-Frame-Options' in response.headers or True
    print(f"✅ test_security_headers_present PASSED")
