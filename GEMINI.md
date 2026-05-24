# Spendly — Expense Tracker

Spendly is a personal finance tracker designed to help users log expenses, understand spending patterns, and take control of their financial life.

## Project Overview

*   **Type:** Flask Web Application (Python)
*   **Aesthetic:** Modern, minimalist "paper" design with a focus on typography and clean spacing.
*   **Key Features:**
    *   Responsive landing page with a video modal ("See how it works").
    *   User authentication (Login/Register) routes (implementation in progress).
    *   Legal pages (Terms and Conditions, Privacy Policy).
    *   Expense management (CRUD operations - implementation in progress).

## Tech Stack

*   **Backend:** Python / Flask
*   **Database:** SQLite (logic in `database/db.py`)
*   **Frontend:**
    *   HTML5 (Jinja2 templates)
    *   CSS3 (Vanilla CSS, custom variables)
    *   JavaScript (Vanilla JS)
*   **Fonts:** DM Serif Display (headings), DM Sans (body)

## Directory Structure

*   `app.py`: Main application entry point and route definitions.
*   `database/`: Database initialization and interaction logic.
    *   `db.py`: SQLite connection and query handling.
*   `static/`: Static assets.
    *   `css/style.css`: Global styles, variables, and shared component styles.
    *   `css/landing.css`: Specific styles for the landing page hero and modal.
    *   `js/main.js`: Global JavaScript.
*   `templates/`: Jinja2 HTML templates.
    *   `base.html`: Main layout with navbar and footer.
    *   `landing.html`: Redesigned landing page with hero section and interactive modal.
    *   `terms.html` & `privacy.html`: Legal documentation pages.
    *   `login.html` & `register.html`: Authentication forms.

## Building and Running

### Prerequisites
*   Python 3.x
*   Dependencies listed in `requirements.txt`

### Setup
1.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Running the App
1.  Start the development server:
    ```bash
    python app.py
    ```
2.  The app runs on `http://127.0.0.1:5001` by default.

## Development Conventions

*   **Styling:** Prefer Vanilla CSS. Use the CSS variables defined in `:root` of `style.css` to maintain brand consistency (colors, spacing, radii).
*   **JavaScript:** Use Vanilla JS for DOM manipulation and interactivity (avoid external libraries unless necessary).
*   **Templates:** All templates should extend `base.html`. Use blocks (`title`, `head`, `content`, `scripts`) to manage page-specific content.
*   **Routing:** Maintain the step-by-step route structure in `app.py`. Ensure new features follow the established naming conventions.
*   **Legal Pages:** Legal pages should use the `.legal-container` class in `style.css` to ensure they follow the centered, readable layout established for the project.
