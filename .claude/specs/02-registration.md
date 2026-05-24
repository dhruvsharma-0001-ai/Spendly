# Spec: Registration

## Overview
This feature implements the user registration flow for Spendly. It allows new users to create an account by providing their name, email, and password. This is a critical building block for personalizing the expense tracking experience and securing user data.

## Depends on
- Step 01: Database Setup

## Routes
- GET /register — Renders the registration form — public
- POST /register — Processes registration data, creates user, and redirects to login — public

## Database changes
No database changes. The `users` table established in Step 01 already contains all necessary columns: `name`, `email`, `password_hash`.

## Templates
- Modify: `templates/register.html` — Ensure the form fields match the database requirements and handle the display of validation errors.

## Files to change
- `app.py`: Implement the logic for `GET` and `POST` methods on the `/register` route.
- `templates/register.html`: Refine the form handling and error display.

## Files to create
No new files.

## New dependencies
No new dependencies. Uses `flask` and `werkzeug.security` (already included).

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with `werkzeug.security.generate_password_hash`
- Use CSS variables establish in `style.css` — never hardcode hex values
- All templates extend `base.html`
- Validate that the email is not already in use before attempting insertion.
- Validate that the password meets a minimum length (e.g., 8 characters).

## Definition of done
- [ ] Accessing `/register` displays the registration form.
- [ ] Submitting the form with a new email successfully creates a user in the `users` table.
- [ ] Passwords are stored as hashes, never in plain text.
- [ ] Submitting an email that already exists displays an appropriate error message ("Email already registered").
- [ ] Submitting a password shorter than 8 characters displays an error message.
- [ ] Upon successful registration, the user is redirected to the `/login` page with a success message (if flash messages are implemented).
- [ ] All database interactions use the `get_db()` helper and parameterized queries.
