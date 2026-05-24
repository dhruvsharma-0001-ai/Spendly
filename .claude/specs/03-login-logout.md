# Spec: Login and Logout

## Overview
This feature implements the authentication system for Spendly. It allows registered users to securely log into their accounts using their email and password, and safely log out. This is a critical step in the roadmap as it enables personalized data management, ensuring that users can only access and modify their own expenses.

## Depends on
- 01-database-setup.md (for the `users` table)
- 02-registration.md (for user accounts)

## Routes
- GET /login — Displays the login form — public
- POST /login — Processes credentials and starts user session — public
- GET /logout — Terminates session and redirects to landing — logged-in

## Database changes
No database changes. Uses existing `users` table.

## Templates
- Modify: `templates/base.html` — Update navbar to show conditional links (Login/Register vs. Profile/Logout).
- Modify: `templates/login.html` — Ensure form aligns with `POST /login` and displays error messages correctly.

## Files to change
- `app.py`:
    - Implement `POST /login` logic.
    - Implement `GET /logout` logic.
    - Set `app.secret_key` for session management.
- `templates/base.html`: Add `if session.user_id` logic to the navbar.
- `templates/login.html`: Wire up error handling and form submission.

## Files to create
No new files.

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs.
- Parameterised queries only.
- Passwords verified with `werkzeug.security.check_password_hash`.
- Use CSS variables — never hardcode hex values.
- All templates extend `base.html`.
- Use Flask's `session` to store `user_id` and `user_name` upon successful login.
- Use `session.clear()` on logout.
- Redirect to `/profile` after successful login.

## Definition of done
- [ ] Navigating to `/login` shows the login form.
- [ ] Entering valid credentials redirects to `/profile`.
- [ ] Entering invalid credentials displays "Invalid email or password" error message.
- [ ] When logged in, navbar shows "Logout" instead of "Login".
- [ ] When logged in, navbar shows "Profile" instead of "Register".
- [ ] Clicking "Logout" clears the session and redirects to the landing page.
- [ ] Logged out users cannot access the `/logout` route (should redirect to `/login`).
- [ ] Logged in users trying to access `/login` are redirected to `/profile`.
