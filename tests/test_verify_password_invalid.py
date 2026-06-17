"""Test: test_verify_password_invalid - Database Utils"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
from database import hash_password, verify_password

def test_verify_password_invalid():
    pwd = 'mysecurepassword'
    hashed = hash_password(pwd)
    assert verify_password(hashed, 'wrongpassword') == False
    print(f"✅ test_verify_password_invalid PASSED")
