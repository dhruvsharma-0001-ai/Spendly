# Spec: Edit Expense

## Overview
This feature allows users to modify existing expense records. It completes the "Update" portion of the CRUD lifecycle, enabling users to correct mistakes or update details like amount, category, date, or description after an entry has been made.

## Depends on
- Step 01: Database Setup (Table structure)
- Step 03: Login and Logout (Authentication/Session management)
- Step 07: Add Expense (Base for expense handling)

## Routes
- `GET /expenses/<int:id>/edit` — Fetches expense details and renders the edit form — Logged-in
- `POST /expenses/<int:id>/edit` — Validates and updates the expense record — Logged-in

## Database changes
No schema changes required. New helper functions needed in `database/db.py`:
- `get_expense(expense_id, user_id)`: Fetches a single expense while ensuring it belongs to the authenticated user.
- `update_expense(expense_id, user_id, amount, category, date, description)`: Updates the record in the `expenses` table.

## Templates
- **Create:** `templates/edit_expense.html` - Form similar to `add_expense.html` but pre-filled with existing data.
- **Modify:** `templates/expenses.html` - Add an "Edit" link/icon to each row in the expense list.

## Files to change
- `app.py`: Implement the `edit_expense` route (GET and POST).
- `database/db.py`: Add `get_expense` and `update_expense` functions.
- `templates/expenses.html`: Add links to the edit route.

## Files to create
- `templates/edit_expense.html`

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug
- Use CSS variables — never hardcode hex values
- All templates extend base.html
- **Security:** Always verify that the `user_id` in the database matches the `user_id` in the session before allowing an edit.

## Definition of done
- [ ] Logged-in user can click "Edit" on an expense in the list.
- [ ] Edit form loads with the current values for amount, category, date, and description.
- [ ] Form submission validates input (positive amount, valid date, required fields).
- [ ] Successful update redirects the user to the expenses list or profile.
- [ ] Changes are reflected in the UI and the database.
- [ ] Attempting to edit an expense ID belonging to another user results in a 403 or redirect with error.
