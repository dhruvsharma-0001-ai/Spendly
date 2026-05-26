# Spec: Delete Expense

## Overview
This feature completes the core CRUD lifecycle for expenses by allowing users to remove existing records. Providing a deletion mechanism is essential for maintaining an accurate financial log and correcting data entry errors. The implementation will include a confirmation step to prevent accidental deletions, ensuring a safe and user-friendly experience.

## Depends on
- 01 Database Setup
- 02 Registration
- 03 Login and Logout
- 05 Backend Routes for Profile Page
- 07 Add Expense
- 08 Edit Expense

## Routes
- POST /expenses/<int:id>/delete — Deletes an expense record — logged-in

*Note: While a GET request for deletion is simpler for a prototype, using POST (or a form-based action) is a safer web practice to prevent accidental or crawler-triggered deletions.*

## Database changes
No database changes. (The existing `expenses` table supports deletion by ID).

## Templates
- Modify: `templates/expenses.html` — Add a "Delete" button or icon next to each expense row.
- Modify: `templates/edit_expense.html` — Add a "Delete Expense" button (typically styled as a danger/secondary action).

## Files to change
- `app.py`: Implement the logic for the `/expenses/<int:id>/delete` route.
- `database/db.py`: Add a `delete_expense(expense_id, user_id)` helper function.
- `templates/expenses.html`: UI updates to include delete triggers.
- `templates/edit_expense.html`: UI updates to include a delete trigger.

## Files to create
No new files.

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug
- Use CSS variables — never hardcode hex values
- All templates extend base.html
- **Authorization:** Always verify that the `user_id` of the expense matches the `session['user_id']` before deleting.
- **Confirmation:** Use a simple JavaScript `confirm()` dialog or a small modal to confirm deletion intent before submitting the request.

## Definition of done
- Navigating to "All Expenses" and clicking a delete button removes the expense from the list.
- Clicking "Delete" from the Edit Expense page removes the expense and redirects the user.
- A confirmation prompt appears before any deletion occurs.
- Attempting to delete an expense belonging to another user (via URL manipulation) fails with an appropriate error message or redirect.
- A success flash message is displayed after a successful deletion.
