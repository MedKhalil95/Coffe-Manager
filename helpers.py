# helpers.py
from flask_login import current_user

def get_current_admin_id():
    """Helper to get current admin ID for filtering queries"""
    if current_user.is_authenticated:
        return current_user.id
    return None

def filter_by_admin(query):
    """Helper to filter queries by current admin"""
    if current_user.is_authenticated:
        return query.filter_by(admin_id=current_user.id)
    return query.filter_by(admin_id=None)  # Will return empty