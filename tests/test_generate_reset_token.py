"""Test: test_generate_reset_token - Database Utils"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
from database import generate_reset_token

def test_generate_reset_token():
    token1 = generate_reset_token()
    token2 = generate_reset_token()
    assert len(token1) > 20
    assert len(token2) > 20
    assert token1 != token2
    print(f"✅ test_generate_reset_token PASSED")
