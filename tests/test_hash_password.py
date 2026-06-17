"""Test: test_hash_password - Database Utils"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
from database import hash_password

def test_hash_password():
    pwd = 'mysecurepassword'
    hashed = hash_password(pwd)
    assert hashed != pwd
    assert len(hashed) > 20
    print(f"✅ test_hash_password PASSED")
