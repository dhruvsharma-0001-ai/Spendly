# Spec: Profile Page Design

## Overview
The profile page serves as the user's dashboard and personal settings hub. It provides an overview of their account information and acts as the central navigation point for managing their financial data. Implementing this now ensures that logged-in users have a functional home base before we build out the expense management features.

## Depends on
Step 03 — Login and Logout

## Routes
- GET /profile — User dashboard and account overview — logged-in

## Database changes
No database changes.

## Templates
- Create: `templates/profile.html`

## Files to change
- `app.py`
- `static/css/style.css`

## Files to create
- `templates/profile.html`

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug
- Use CSS variables — never hardcode hex values
- All templates extend base.html

## Definition of done
- [ ] Visiting `/profile` while logged out redirects to `/login`.
- [ ] Visiting `/profile` while logged in displays the user's name and email from the database.
- [ ] The page shows a summary of account information (e.g., "Member since").
- [ ] The page contains a "Recent Activity" section with a list of the 5 most recent expenses.
- [ ] The design uses the `.profile-container` class and adheres to the "paper" aesthetic.
- [ ] Logout link is visible and functional on the profile page.
