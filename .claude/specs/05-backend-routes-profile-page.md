# Spec: Backend Routes for Profile Page

## Overview
This feature extends the profile dashboard with more comprehensive data insights and a dedicated view for all historical transactions. While the initial profile page provided a basic overview, this step adds analytical summaries—such as total spending and category breakdown—and implements the "All Expenses" list page. This ensures users can access and review their full financial history beyond the most recent items.

## Depends on
Step 04 — Profile Page Design

## Routes
- GET /expenses — Full list of user expenses — logged-in

## Database changes
No database changes.

## Templates
- Create: `templates/expenses.html`
- Modify: `templates/profile.html` — Add links to the full list and display new statistics.

## Files to change
- `app.py`
- `templates/profile.html`

## Files to create
- `templates/expenses.html`

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug
- Use CSS variables — never hardcode hex values
- All templates extend base.html

## Definition of done
- [ ] The `/profile` route calculates and passes `total_spent` and `top_category` to the template.
- [ ] The profile page displays the total spent amount formatted as currency (₹).
- [ ] The profile page identifies and displays the category where the user has the highest number of expenses.
- [ ] The `/expenses` route is implemented and only accessible to logged-in users.
- [ ] The `/expenses` page lists every expense record for the current user in reverse chronological order.
- [ ] The "View all" link in the "Recent Activity" section of the profile page correctly links to `/expenses`.
- [ ] All database queries are parameterized and database connections are properly closed.
