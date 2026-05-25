# Spec: Date Filter Profile

## Overview
As users accumulate expenses over multiple months, an all-time summary becomes less actionable for day-to-day budgeting. This feature introduces a month and year filter to the profile dashboard. By defaulting to the current month and allowing users to select past months, the dashboard transforms from a static historical view into a dynamic monthly budgeting tool.

## Depends on
Step 05 — Backend Routes for Profile Page

## Routes
No new routes.
Modify existing GET `/profile` route to accept optional `month` and `year` query parameters.

## Database changes
No database changes.

## Templates
- Modify: `templates/profile.html` — Add a form with a month/year selector that submits a GET request to filter the dashboard data.

## Files to change
- `app.py`
- `templates/profile.html`
- `static/css/style.css` (if necessary to style the filter form)

## Files to create
No new files.

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only. Use `LIKE ?` with `'YYYY-MM-%'` for date filtering to ensure compatibility with SQLite string dates.
- Passwords hashed with werkzeug
- Use CSS variables — never hardcode hex values
- All templates extend base.html
- If no month/year is provided in the query string, default to the current month and year using Python's `datetime` module.

## Definition of done
- [ ] The `/profile` route accepts `month` and `year` query parameters via `request.args`.
- [ ] If `month` and `year` are missing or invalid, the route defaults to the current month and year.
- [ ] The `total_spent`, `top_category`, `category_data` chart, and `recent_expenses` list all filter their data based on the selected (or default) month and year.
- [ ] `templates/profile.html` includes a form (method="GET") with a `<select>` or `<input type="month">` to choose the date range.
- [ ] The filter form automatically selects/displays the currently active month and year.
- [ ] Changing the filter and submitting updates the page URL and reflects the filtered data correctly.
