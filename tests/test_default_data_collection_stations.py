"""Test: test_default_data_collection_stations - Database Utils"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
from database import default_data_collection_stations

def test_default_data_collection_stations():
    stations = default_data_collection_stations()
    assert len(stations) > 0
    assert 'no' in stations[0]
    assert 'name' in stations[0]
    print(f"✅ test_default_data_collection_stations PASSED")
