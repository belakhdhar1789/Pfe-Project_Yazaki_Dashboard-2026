"""Test: test_verify_password_empty_stored - Database Utils"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
from database import verify_password

def test_verify_password_empty_stored():
    assert verify_password('', 'anypassword') == False
    print(f"✅ test_verify_password_empty_stored PASSED")
