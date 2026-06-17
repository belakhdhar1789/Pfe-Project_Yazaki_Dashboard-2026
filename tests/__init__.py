"""
Yazaki PFE 2026 - Test Suite
Individual test modules for the manufacturing dashboard project
Each test file is independently runnable with: pytest test_name.py
"""

from .test_register_valid import *
from .test_register_missing_fields import *
from .test_login_valid_admin import *
from .test_login_invalid_password import *
from .test_login_nonexistent_user import *
from .test_login_pending_user import *
from .test_hash_password import *
from .test_verify_password_valid import *
from .test_verify_password_invalid import *
from .test_verify_password_empty_stored import *
from .test_generate_reset_token import *
from .test_is_legacy_password_hash import *
from .test_default_data_collection_stations import *
from .test_normalize_data_collection_stations import *
from .test_get_table_config_not_authenticated import *
from .test_get_table_config_authenticated import *
from .test_get_dashboard_not_authenticated import *
from .test_session_cookie_httponly import *
from .test_security_headers_present import *
from .test_data_collection_settings_exist import *
from .test_user_registration_to_login_flow import *
from .test_multiple_requests_same_client import *

__all__ = [
    'test_register_valid',
    'test_register_missing_fields',
    'test_login_valid_admin',
    'test_login_invalid_password',
    'test_login_nonexistent_user',
    'test_login_pending_user',
    'test_hash_password',
    'test_verify_password_valid',
    'test_verify_password_invalid',
    'test_verify_password_empty_stored',
    'test_generate_reset_token',
    'test_is_legacy_password_hash',
    'test_default_data_collection_stations',
    'test_normalize_data_collection_stations',
    'test_get_table_config_not_authenticated',
    'test_get_table_config_authenticated',
    'test_get_dashboard_not_authenticated',
    'test_session_cookie_httponly',
    'test_security_headers_present',
    'test_data_collection_settings_exist',
    'test_user_registration_to_login_flow',
    'test_multiple_requests_same_client',
]
