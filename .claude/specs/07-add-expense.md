# Spec: Add Expense

## Overview
This feature allows logged-in users to record new expenses by providing an amount, category, date, and an optional description. It is a fundamental part of the expense management system, enabling users to build their spending history and populate the dashboard and profile views.

## Depends on
- 01-database-setup.md
- 03-login-logout.md
- 05-backend-routes-profile-page.md

## Routes
- GET /expenses/add — Displays the form to add a new expense — Logged-in
- POST /expenses/add — Processes the form submission and inserts the expense into the database — Logged-in

## Database changes
No database changes. The `expenses` table already contains the necessary columns: `id`, `user_id`, `amount`, `category`, `date`, `description`, and `created_at`.

## Templates
- Create: `templates/add_expense.html` — Contains the form for adding an expense.
- Modify: `templates/profile.html` — Add an "Add Expense" button/link in the header or sidebar.
- Modify: `templates/expenses.html` — Add an "Add Expense" button/link.

## Files to change
- `app.py`: Implement GET and POST logic for `/expenses/add`.
- `templates/profile.html`: Add navigation link to the add expense form.
- `templates/expenses.html`: Add navigation link to the add expense form.
- `static/css/style.css`: Add styles for the form if specific styling is needed (using established CSS variables).

## Files to create
- `templates/add_expense.html`

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug
- Use CSS variables — never hardcode hex values
- All templates extend base.html

## Definition of done
- Logged-in user can access `/expenses/add`.
- Form validation:
    - Amount is required and must be a positive number.
    - Category is required (selection from a predefined list or text input).
    - Date is required (defaults to today).
- Successful submission redirects the user to the Profile or Expenses page.
- The new expense appears in the "Recent Expenses" list on the Profile page (if it falls within the current date filter).
- The new expense appears in the "All Expenses" list.
- An error message is displayed if the form is submitted with missing or invalid data.
