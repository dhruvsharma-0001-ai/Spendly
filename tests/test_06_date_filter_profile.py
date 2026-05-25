"""
Tests for Step 06: Date Filter Profile
Based on .claude/specs/06-date-filter-profile.md

Spec Behaviors Tested:
1. /profile route accepts month and year query parameters.
2. /profile defaults to the current month and year if missing or invalid.
3. /profile filters all dashboard data based on the selected/default date.
4. /profile template displays the currently active month and year in the form.
"""

import pytest
import uuid
from datetime import datetime
from app import app
from database.db import init_db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            from database.db import get_db
            conn = get_db()
            cursor = conn.cursor()
            
            # Create user with unique email
            unique_email = f"test_{uuid.uuid4().hex[:8]}@spendly.com"
            cursor.execute("INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                           ('Test User', unique_email, 'scrypt:32768:8:1$random$hash'))
            user_id = cursor.lastrowid
            
            # Create expenses spread across different months
            now = datetime.now()
            current_month = f"{now.year}-{now.month:02d}"
            past_month = f"{now.year}-{now.month - 1:02d}" if now.month > 1 else f"{now.year - 1}-12"
            
            expenses = [
                # Current month expenses
                (user_id, 100.0, 'Food', f'{current_month}-01', 'Current Month Burger'),
                (user_id, 50.0, 'Food', f'{current_month}-05', 'Current Month Fries'),
                (user_id, 200.0, 'Transport', f'{current_month}-10', 'Current Month Taxi'),
                
                # Past month expenses
                (user_id, 500.0, 'Shopping', f'{past_month}-15', 'Past Month Shoes'),
            ]
            cursor.executemany(
                "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
                expenses
            )
            conn.commit()
            conn.close()
            
            app.config['TEST_USER_ID'] = user_id
            app.config['CURRENT_MONTH'] = current_month
            app.config['PAST_MONTH'] = past_month
            
        yield client

def login(client, user_id):
    """Helper to mock login by setting session directly"""
    with client.session_transaction() as sess:
        sess['user_id'] = user_id
        sess['user_name'] = 'Test User'

def test_profile_default_current_month(client):
    """Verify /profile defaults to current month and filters data accordingly"""
    login(client, app.config['TEST_USER_ID'])
    response = client.get('/profile')
    
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    
    # Should show current month expenses
    assert 'Current Month Burger' in html
    assert 'Current Month Taxi' in html
    # Should NOT show past month expenses
    assert 'Past Month Shoes' not in html
    
    # Total spent: 100 + 50 + 200 = 350.00
    assert '₹350.00' in html
    
    # Check default filter value in the input
    # Look for value="YYYY-MM"
    assert f'value="{app.config["CURRENT_MONTH"]}"' in html

def test_profile_filter_past_month(client):
    """Verify /profile respects month_year query parameter"""
    login(client, app.config['TEST_USER_ID'])
    past_month_str = app.config['PAST_MONTH'] # e.g., '2026-04'
    
    response = client.get(f'/profile?month_year={past_month_str}')
    
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    
    # Should show past month expenses
    assert 'Past Month Shoes' in html
    # Should NOT show current month expenses
    assert 'Current Month Burger' not in html
    
    # Total spent: 500.00
    assert '₹500.00' in html
    
    # Top Category should be Shopping
    assert 'Shopping' in html
    
    # Input should retain selected value
    assert f'value="{past_month_str}"' in html

def test_profile_invalid_date_fallback(client):
    """Verify invalid query params gracefully fall back to current month"""
    login(client, app.config['TEST_USER_ID'])
    response = client.get('/profile?month_year=invalid-date')
    
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    
    # Should fall back to current month
    assert 'Current Month Burger' in html
    assert '₹350.00' in html
    assert f'value="{app.config["CURRENT_MONTH"]}"' in html

"""
Summary of Tests:
- test_profile_default_current_month: Verifies missing query params default to current month and filter data properly.
- test_profile_filter_past_month: Verifies passing a month_year param correctly filters the stats and recent activity.
- test_profile_invalid_date_fallback: Verifies garbage input falls back to the current month without crashing.
"""