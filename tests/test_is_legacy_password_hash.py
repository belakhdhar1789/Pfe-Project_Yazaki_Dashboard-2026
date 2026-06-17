"""Test: test_is_legacy_password_hash - Database Utils"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
from database import hash_password, is_legacy_password_hash

def test_is_legacy_password_hash():
    modern_hash = hash_password('test')
    assert is_legacy_password_hash(modern_hash) == False
    assert is_legacy_password_hash('abc123def456') == True
    assert is_legacy_password_hash('') == False
    print(f"✅ test_is_legacy_password_hash PASSED")
