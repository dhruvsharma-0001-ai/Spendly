from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import init_db, seed_db, get_db
import sqlite3

app = Flask(__name__)
app.secret_key = 'dev-secret-key-for-spendly-step-03'

# Initialize database
with app.app_context():
    init_db()
    seed_db()


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        if not name or not email or not password:
            error = "All fields are required."
        elif len(password) < 8:
            error = "Password must be at least 8 characters long."
        else:
            db = get_db()
            cursor = db.cursor()
            
            # Check if email is already registered
            cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
            if cursor.fetchone() is not None:
                error = "Email already registered."
            else:
                # Insert new user
                password_hash = generate_password_hash(password)
                try:
                    cursor.execute(
                        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                        (name, email, password_hash)
                    )
                    db.commit()
                    return redirect(url_for('login', success="Account created successfully. Please sign in."))
                except sqlite3.Error as e:
                    error = "An error occurred while creating your account."
                finally:
                    db.close()

    return render_template("register.html", error=error)


@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for('profile'))

    success = request.args.get('success')
    error = None

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            error = "Both email and password are required."
        else:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT id, name, password_hash FROM users WHERE email = ?", (email,))
            user = cursor.fetchone()
            db.close()

            if user and check_password_hash(user['password_hash'], password):
                session['user_id'] = user['id']
                session['user_name'] = user['name']
                return redirect(url_for('profile'))
            else:
                error = "Invalid email or password"

    return render_template("login.html", success=success, error=error)


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/logout")
def logout():
    if "user_id" not in session:
        return redirect(url_for('login'))
    session.clear()
    return redirect(url_for('landing'))


@app.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect(url_for('login'))
        
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("SELECT name, email, created_at FROM users WHERE id = ?", (session['user_id'],))
    user = cursor.fetchone()
    
    cursor.execute("SELECT amount, category, date, description FROM expenses WHERE user_id = ? ORDER BY date DESC, id DESC LIMIT 5", (session['user_id'],))
    recent_expenses = cursor.fetchall()

    cursor.execute("SELECT SUM(amount) FROM expenses WHERE user_id = ?", (session['user_id'],))
    total_spent = cursor.fetchone()[0] or 0.0

    cursor.execute("SELECT category, COUNT(*) as count FROM expenses WHERE user_id = ? GROUP BY category ORDER BY count DESC LIMIT 1", (session['user_id'],))
    top_category_row = cursor.fetchone()
    top_category = top_category_row['category'] if top_category_row else "None"

    cursor.execute("SELECT category, SUM(amount) as total FROM expenses WHERE user_id = ? GROUP BY category ORDER BY total DESC", (session['user_id'],))
    category_data = cursor.fetchall()
    
    db.close()
    
    return render_template("profile.html", 
                           user=user, 
                           recent_expenses=recent_expenses, 
                           total_spent=total_spent, 
                           top_category=top_category, 
                           category_data=category_data)


@app.route("/expenses")
def expenses():
    if "user_id" not in session:
        return redirect(url_for('login'))
        
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("SELECT id, amount, category, date, description FROM expenses WHERE user_id = ? ORDER BY date DESC, id DESC", (session['user_id'],))
    all_expenses = cursor.fetchall()
    
    db.close()
    
    return render_template("expenses.html", expenses=all_expenses)


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    app.run(debug=True, port=5001)
