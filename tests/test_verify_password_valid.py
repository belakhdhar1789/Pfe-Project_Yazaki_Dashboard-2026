"""Test: test_verify_password_valid - Database Utils"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
from database import hash_password, verify_password

def test_verify_password_valid():
    pwd = 'mysecurepassword'
    hashed = hash_password(pwd)
    assert verify_password(hashed, pwd) == True
    print(f"✅ test_verify_password_valid PASSED")
