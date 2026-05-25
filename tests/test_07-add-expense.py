"""
Tests for Step 07: Add Expense
Verification of expense creation, validation, and authorization.
Based on .claude/specs/07-add-expense.md
"""

import pytest
import os
import tempfile
import database.db
from app import app
from database.db import init_db, get_db
from werkzeug.security import generate_password_hash
from datetime import datetime

@pytest.fixture
def client():
    """
    Test client fixture with a temporary file-based database.
    Ensures isolation and persistence across multiple connections in a single test.
    """
    db_fd, db_path = tempfile.mkstemp()
    app.config['TESTING'] = True
    
    # Monkeypatch the DATABASE variable in database.db module
    original_db = database.db.DATABASE
    database.db.DATABASE = db_path
    
    with app.test_client() as client:
        with app.app_context():
            init_db()
            # Create a test user for authentication tests
            db = get_db()
            db.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                ("Test User", "test@example.com", generate_password_hash("password123"))
            )
            db.commit()
            db.close()
        yield client

    # Cleanup
    os.close(db_fd)
    if os.path.exists(db_path):
        os.unlink(db_path)
    database.db.DATABASE = original_db

def login(client, email, password):
    """Helper function to log in a user."""
    return client.post('/login', data={'email': email, 'password': password}, follow_redirects=True)

def test_add_expense_route_auth_guard(client):
    """
    Verify that /expenses/add redirects to login for unauthenticated users.
    Requirement: GET /expenses/add — Logged-in
    """
    response = client.get('/expenses/add', follow_redirects=False)
    assert response.status_code == 302
    assert '/login' in response.headers['Location']

def test_add_expense_post_auth_guard(client):
    """
    Verify that POST /expenses/add redirects to login for unauthenticated users.
    Requirement: POST /expenses/add — Logged-in
    """
    response = client.post('/expenses/add', data={'amount': '100', 'category': 'Food', 'date': '2023-01-01'}, follow_redirects=False)
    assert response.status_code == 302
    assert '/login' in response.headers['Location']

def test_add_expense_page_loads_for_logged_in_user(client):
    """
    Verify that a logged-in user can access the add expense page.
    Requirement: Logged-in user can access /expenses/add.
    """
    login(client, "test@example.com", "password123")
    response = client.get('/expenses/add')
    assert response.status_code == 200
    assert b"Add Expense" in response.data
    # Check if form exists
    assert b'method="POST"' in response.data
    assert b'name="amount"' in response.data
    assert b'name="category"' in response.data
    assert b'name="date"' in response.data

def test_add_expense_form_default_date(client):
    """
    Verify that the add expense form defaults the date to today.
    Requirement: Date is required (defaults to today).
    """
    login(client, "test@example.com", "password123")
    today = datetime.now().strftime('%Y-%m-%d')
    response = client.get('/expenses/add')
    assert f'value="{today}"'.encode() in response.data

def test_add_expense_success(client):
    """
    Verify that a valid expense can be added successfully.
    Requirement: Successful submission redirects the user to the Profile or Expenses page.
    """
    login(client, "test@example.com", "password123")
    
    expense_data = {
        'amount': '1500.50',
        'category': 'Dining',
        'date': '2023-10-27',
        'description': 'Dinner with friends'
    }
    
    # Follow redirects to see where it ends up
    response = client.post('/expenses/add', data=expense_data, follow_redirects=True)
    
    # Check redirect (should be to profile or expenses as per spec)
    assert response.status_code == 200
    assert b"Profile" in response.data or b"Recent Activity" in response.data
    
    # Verify DB state
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM expenses WHERE amount = 1500.50 AND category = 'Dining'")
        expense = cursor.fetchone()
        assert expense is not None
        assert expense['description'] == 'Dinner with friends'
        assert expense['date'] == '2023-10-27'
        db.close()

def test_add_expense_missing_amount(client):
    """
    Verify that amount is required.
    Requirement: Amount is required and must be a positive number.
    """
    login(client, "test@example.com", "password123")
    
    expense_data = {
        'amount': '',
        'category': 'Dining',
        'date': '2023-10-27'
    }
    
    response = client.post('/expenses/add', data=expense_data)
    # Check for error message
    assert b"Amount, category, and date are required." in response.data or b"required" in response.data.lower()

def test_add_expense_invalid_amount_zero(client):
    """
    Verify that amount must be positive (not zero).
    Requirement: Amount must be a positive number.
    """
    login(client, "test@example.com", "password123")
    
    expense_data = {
        'amount': '0',
        'category': 'Dining',
        'date': '2023-10-27'
    }
    
    response = client.post('/expenses/add', data=expense_data)
    assert b"Amount must be a positive number." in response.data

def test_add_expense_invalid_amount_negative(client):
    """
    Verify that amount must be positive (not negative).
    Requirement: Amount must be a positive number.
    """
    login(client, "test@example.com", "password123")
    
    expense_data = {
        'amount': '-50',
        'category': 'Dining',
        'date': '2023-10-27'
    }
    
    response = client.post('/expenses/add', data=expense_data)
    assert b"Amount must be a positive number." in response.data

def test_add_expense_invalid_amount_text(client):
    """
    Verify that amount must be a number.
    Requirement: Amount must be a positive number.
    """
    login(client, "test@example.com", "password123")
    
    expense_data = {
        'amount': 'abc',
        'category': 'Dining',
        'date': '2023-10-27'
    }
    
    response = client.post('/expenses/add', data=expense_data)
    # The implementation says "Invalid amount format."
    assert b"Invalid amount or date format." in response.data or b"number" in response.data.lower()

def test_add_expense_missing_category(client):
    """
    Verify that category is required.
    Requirement: Category is required.
    """
    login(client, "test@example.com", "password123")
    
    expense_data = {
        'amount': '100',
        'category': '',
        'date': '2023-10-27'
    }
    
    response = client.post('/expenses/add', data=expense_data)
    assert b"Amount, category, and date are required." in response.data or b"required" in response.data.lower()

def test_add_expense_persistence_and_profile_visibility(client):
    """
    Verify that a new expense appears on the profile page.
    Requirement: The new expense appears in the "Recent Expenses" list on the Profile page.
    """
    login(client, "test@example.com", "password123")
    
    # Use today's date to ensure it appears in the default filter
    today = datetime.now().strftime('%Y-%m-%d')
    unique_desc = "Test Unique Expense Persistence"
    
    expense_data = {
        'amount': '999.99',
        'category': 'TestCat',
        'date': today,
        'description': unique_desc
    }
    
    client.post('/expenses/add', data=expense_data, follow_redirects=True)
    
    # Go to profile
    response = client.get('/profile')
    assert unique_desc.encode() in response.data
    assert b"999.99" in response.data
    # Check for currency symbol (UTF-8 for ₹)
    assert b"\xe2\x82\xb9" in response.data or "₹".encode() in response.data

def test_add_expense_invalid_date_format(client):
    """
    Verify that an invalid date format is rejected.
    Requirement: Date is required and must be in YYYY-MM-DD format.
    """
    login(client, "test@example.com", "password123")
    
    expense_data = {
        'amount': '100',
        'category': 'Dining',
        'date': '2023-13-45' # Invalid date
    }
    
    response = client.post('/expenses/add', data=expense_data)
    assert b"Invalid amount or date format." in response.data

def test_add_expense_all_expenses_visibility(client):
    """
    Verify that a new expense appears in the All Expenses list.
    Requirement: The new expense appears in the "All Expenses" list.
    """
    login(client, "test@example.com", "password123")
    
    unique_desc = "All Expenses Visibility Check"
    expense_data = {
        'amount': '123.45',
        'category': 'Other',
        'date': '2020-01-01', # Old date, might not show in recent but should show in all
        'description': unique_desc
    }
    
    client.post('/expenses/add', data=expense_data, follow_redirects=True)
    
    # Go to expenses page
    response = client.get('/expenses')
    assert unique_desc.encode() in response.data
    assert b"123.45" in response.data
