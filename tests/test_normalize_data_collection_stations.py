"""Test: test_normalize_data_collection_stations - Database Utils"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
from database import normalize_data_collection_stations

def test_normalize_data_collection_stations():
    stations = [{'no': 1, 'name': 'WS1'}, {'no': 2, 'name': 'WS2'}]
    normalized = normalize_data_collection_stations(stations)
    assert len(normalized) == 2
    assert normalized[0]['no'] == 1
    assert normalized[0]['name'] == 'WS1'
    print(f"✅ test_normalize_data_collection_stations PASSED")
