"""Test: test_session_cookie_httponly - Security"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c

def test_session_cookie_httponly(client):
    response = client.get('/')
    if 'Set-Cookie' in response.headers:
        assert 'HttpOnly' in response.headers['Set-Cookie'] or 'HttpOnly' in str(response.headers)
    print(f"✅ test_session_cookie_httponly PASSED")
