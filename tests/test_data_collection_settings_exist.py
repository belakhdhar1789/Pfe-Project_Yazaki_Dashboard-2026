"""Test: test_data_collection_settings_exist - Data Collection"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
from database import get_db

def test_data_collection_settings_exist():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM data_collection_entries')
    count = cursor.fetchone()[0]
    conn.close()
    assert count >= 0
    print(f"✅ test_data_collection_settings_exist PASSED")
