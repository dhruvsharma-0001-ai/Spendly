"""
Tests for Step 08: Edit Expense
Verification of expense modification, validation, and authorization.
Based on .claude/specs/08-edit-expense.md
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
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    # Monkeypatch the DATABASE variable in database.db module
    original_db = database.db.DATABASE
    database.db.DATABASE = db_path
    
    with app.test_client() as client:
        with app.app_context():
            init_db()
            db = get_db()
            # Create two test users for authorization tests
            db.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                ("User One", "user1@example.com", generate_password_hash("password123"))
            )
            user1_id = 1
            
            db.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                ("User Two", "user2@example.com", generate_password_hash("password123"))
            )
            user2_id = 2
            
            # Add an expense for User One (using valid category 'Bills')
            db.execute(
                "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
                (user1_id, 1000.0, "Bills", "2023-10-01", "Electricity bill")
            )
            
            # Add an expense for User Two
            db.execute(
                "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
                (user2_id, 500.0, "Food", "2023-10-02", "Grocery")
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

def test_edit_expense_auth_guard(client):
    """
    Verify that /expenses/<id>/edit redirects to login for unauthenticated users.
    Requirement: GET /expenses/<id>/edit — Logged-in
    """
    response = client.get('/expenses/1/edit', follow_redirects=False)
    assert response.status_code == 302
    assert '/login' in response.headers['Location']

def test_edit_expense_page_loads_for_owner(client):
    """
    Verify that a logged-in user can access the edit page for their own expense.
    Requirement: Logged-in user can view the edit form for their own expense.
    """
    login(client, "user1@example.com", "password123")
    response = client.get('/expenses/1/edit')
    assert response.status_code == 200
    assert b"Edit Expense" in response.data
    assert b'value="1000.0"' in response.data
    assert b'Bills' in response.data
    assert b'value="2023-10-01"' in response.data
    assert b"Electricity bill" in response.data

def test_edit_expense_form_prefilled(client):
    """
    Verify that the form is pre-filled with the correct existing data.
    Requirement: Form is pre-filled with correct data.
    """
    login(client, "user2@example.com", "password123")
    response = client.get('/expenses/2/edit')
    assert response.status_code == 200
    assert b'value="500.0"' in response.data
    assert b'Food' in response.data
    assert b'value="2023-10-02"' in response.data
    assert b"Grocery" in response.data

def test_edit_expense_success(client):
    """
    Verify that submitting valid changes updates the database and redirects.
    Requirement: Submitting valid changes updates the database and redirects to /expenses.
    """
    login(client, "user1@example.com", "password123")
    
    updated_data = {
        'amount': '1200.50',
        'category': 'Transport',
        'date': '2023-10-05',
        'description': 'Updated electricity bill'
    }
    
    response = client.post('/expenses/1/edit', data=updated_data, follow_redirects=True)
    
    # Check redirect to /expenses
    assert response.status_code == 200
    assert b"All Expenses" in response.data
    assert b"Expense updated successfully!" in response.data
    
    # Verify DB update
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM expenses WHERE id = 1")
        expense = cursor.fetchone()
        assert float(expense['amount']) == 1200.50
        assert expense['category'] == 'Transport'
        assert expense['date'] == '2023-10-05'
        assert expense['description'] == 'Updated electricity bill'
        db.close()

def test_edit_expense_invalid_amount_negative(client):
    """
    Verify that validation works for negative amounts.
    Requirement: Input validation works (e.g., negative amount).
    """
    login(client, "user1@example.com", "password123")
    
    invalid_data = {
        'amount': '-100',
        'category': 'Bills',
        'date': '2023-10-01',
        'description': 'Electricity bill'
    }
    
    response = client.post('/expenses/1/edit', data=invalid_data)
    assert b"Amount must be a positive number." in response.data
    
    # Verify DB NOT updated
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT amount FROM expenses WHERE id = 1")
        expense = cursor.fetchone()
        assert float(expense['amount']) == 1000.0
        db.close()

def test_edit_expense_unauthorized_access(client):
    """
    Verify that a user cannot edit an expense belonging to another user.
    Requirement: A user cannot edit an expense belonging to another user.
    """
    # Log in as User One
    login(client, "user1@example.com", "password123")
    
    # Try to access User Two's expense (ID 2)
    response = client.get('/expenses/2/edit', follow_redirects=True)
    
    # Should redirect with error
    assert b"Expense not found or unauthorized." in response.data
    assert b"All Expenses" in response.data

def test_edit_expense_unauthorized_post(client):
    """
    Verify that a user cannot update an expense belonging to another user via POST.
    Requirement: A user cannot edit an expense belonging to another user.
    """
    # Log in as User One
    login(client, "user1@example.com", "password123")
    
    # Try to POST to User Two's expense (ID 2)
    updated_data = {
        'amount': '9999',
        'category': 'Bills',
        'date': '2023-10-05',
        'description': 'I am hacking'
    }
    response = client.post('/expenses/2/edit', data=updated_data, follow_redirects=True)
    
    # Should redirect with error
    assert b"Expense not found or unauthorized." in response.data
    
    # Verify DB NOT updated
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM expenses WHERE id = 2")
        expense = cursor.fetchone()
        assert float(expense['amount']) == 500.0 # Remains unchanged
        assert expense['category'] == 'Food'
        db.close()

def test_edit_expense_non_existent(client):
    """
    Verify that trying to edit a non-existent expense results in an error.
    Requirement: Attempting to edit an expense ID belonging to another user results in a 403 or redirect with error.
    """
    login(client, "user1@example.com", "password123")
    
    response = client.get('/expenses/999/edit', follow_redirects=True)
    assert b"Expense not found or unauthorized." in response.data
