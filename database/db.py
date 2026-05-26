import sqlite3
from werkzeug.security import generate_password_hash

DATABASE = 'spendly.db'

def get_db():
    """Returns a SQLite connection with row_factory and foreign keys enabled."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    """Creates all tables using CREATE TABLE IF NOT EXISTS."""
    conn = get_db()
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        )
    ''')

    # Create expenses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            description TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    conn.commit()
    conn.close()

def seed_db():
    """Inserts sample data for development if the database is empty."""
    conn = get_db()
    cursor = conn.cursor()

    # Check if we already have data
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]

    if count > 0:
        conn.close()
        return

    # Seed demo user
    demo_password_hash = generate_password_hash('demo123')
    cursor.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ('Demo User', 'demo@spendly.com', demo_password_hash)
    )
    user_id = cursor.lastrowid

    # Seed sample expenses
    sample_expenses = [
        (user_id, 1200.50, 'Food', '2026-05-20', 'Weekly groceries'),
        (user_id, 4500.00, 'Bills', '2026-05-01', 'Monthly electricity bill'),
        (user_id, 800.00, 'Transport', '2026-05-15', 'Fuel refill'),
        (user_id, 1500.00, 'Health', '2026-05-10', 'Routine checkup'),
        (user_id, 2000.00, 'Shopping', '2026-05-18', 'New sneakers'),
        (user_id, 500.00, 'Entertainment', '2026-05-22', 'Movie night'),
        (user_id, 300.00, 'Other', '2026-05-12', 'Small stationery items'),
        (user_id, 650.75, 'Food', '2026-05-23', 'Dinner outing')
    ]

    cursor.executemany(
        "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
        sample_expenses
    )

    conn.commit()
    conn.close()

def add_expense(user_id, amount, category, date, description):
    """Inserts a new expense into the database with proper resource cleanup."""
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
            (user_id, amount, category, date, description)
        )
        conn.commit()
    finally:
        conn.close()

def get_expense(expense_id, user_id):
    """Fetches a single expense while ensuring it belongs to the authenticated user."""
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, amount, category, date, description FROM expenses WHERE id = ? AND user_id = ?",
            (expense_id, user_id)
        )
        return cursor.fetchone()
    finally:
        conn.close()

def update_expense(expense_id, user_id, amount, category, date, description):
    """Updates an existing expense record while ensuring it belongs to the authenticated user."""
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE expenses SET amount = ?, category = ?, date = ?, description = ? WHERE id = ? AND user_id = ?",
            (amount, category, date, description, expense_id, user_id)
        )
        conn.commit()
    finally:
        conn.close()

def delete_expense(expense_id, user_id):
    """Deletes an expense record while ensuring it belongs to the authenticated user."""
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM expenses WHERE id = ? AND user_id = ?",
            (expense_id, user_id)
        )
        conn.commit()
    finally:
        conn.close()
