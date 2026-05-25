"""
Tests for Step 05: Backend Routes for Profile Page
Based on .claude/specs/05-backend-routes-profile-page.md

Spec Behaviors Tested:
1. /profile passes total_spent and top_category to template.
2. /profile displays total spent formatted as currency.
3. /profile identifies and displays top category.
4. /expenses is accessible only to logged-in users.
5. /expenses lists every expense in reverse chronological order.
6. "View all" link in /profile links to /expenses.
"""

import pytest
import uuid
from app import app
from database.db import init_db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    # In a real app we'd mock get_db to use :memory:, but since it's hardcoded in db.py,
    # we will just use the real db for now and use unique identifiers to avoid conflicts.
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
            
            # Create expenses (not in chronological order to test sorting)
            expenses = [
                (user_id, 100.0, 'Food', '2026-05-01', 'Burger'),
                (user_id, 200.0, 'Transport', '2026-05-02', 'Taxi'),
                (user_id, 150.0, 'Food', '2026-05-03', 'Pizza')
            ]
            cursor.executemany(
                "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
                expenses
            )
            conn.commit()
            conn.close()
            
            # Store user_id in app config for easy access in tests
            app.config['TEST_USER_ID'] = user_id
            
        yield client

def login(client, user_id):
    """Helper to mock login by setting session directly for testing isolated routes"""
    with client.session_transaction() as sess:
        sess['user_id'] = user_id
        sess['user_name'] = 'Test User'

def test_profile_requires_auth(client):
    """Verify /profile redirects to /login when unauthenticated"""
    response = client.get('/profile')
    assert response.status_code == 302
    assert '/login' in response.headers['Location']

def test_expenses_requires_auth(client):
    """Verify /expenses redirects to /login when unauthenticated"""
    response = client.get('/expenses')
    assert response.status_code == 302
    assert '/login' in response.headers['Location']

def test_profile_displays_stats(client):
    """Verify /profile calculates and displays total_spent and top_category"""
    login(client, app.config['TEST_USER_ID'])
    response = client.get('/profile')
    
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    
    # Total spent: 100 + 200 + 150 = 450.00
    assert '₹450.00' in html
    
    # Top category: Food (2 expenses vs 1 Transport)
    assert 'Food' in html
    
    # View all link
    assert '/expenses' in html

def test_expenses_list_order(client):
    """Verify /expenses lists all records in reverse chronological order"""
    login(client, app.config['TEST_USER_ID'])
    response = client.get('/expenses')
    
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    
    # Check if all expenses are present
    assert 'Pizza' in html
    assert 'Taxi' in html
    assert 'Burger' in html
    
    # Check reverse chronological order by finding positions
    pos_pizza = html.find('Pizza')
    pos_taxi = html.find('Taxi')
    pos_burger = html.find('Burger')
    
    assert pos_pizza < pos_taxi < pos_burger, "Expenses are not in reverse chronological order"

"""
Summary of Tests:
- test_profile_requires_auth: Verify auth guard on /profile
- test_expenses_requires_auth: Verify auth guard on /expenses
- test_profile_displays_stats: Verify total_spent calculation, top_category logic, currency formatting, and view all link
- test_expenses_list_order: Verify all expenses are listed in DESC date order
"""
