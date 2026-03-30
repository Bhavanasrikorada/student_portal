from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
print("THIS IS THE NEW APP VERSION")
app = Flask(__name__)
app.secret_key = "secret123"

# ---------- DATABASE ----------
def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

def create_table():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_number TEXT UNIQUE,
            email TEXT,
            password TEXT
        )
    """)

    conn.commit()
    conn.close()

create_table()

# ---------- HELPER ----------
def is_logged_in():
    return "user" in session

print("ALL ROUTES STARTING")
# ---------- ROUTES ----------

@app.route("/")
def home():
    if is_logged_in():
        return redirect(url_for("dashboard"))
    return render_template("login.html")


# ---------- REGISTER ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    if is_logged_in():
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        roll = request.form["roll"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])

        conn = get_db()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO students (roll_number, email, password) VALUES (?, ?, ?)",
                (roll, email, password)
            )
            conn.commit()
        except:
            conn.close()
            return render_template("register.html", error="Roll number already exists!")

        conn.close()
        return redirect(url_for("home"))

    return render_template("register.html")


# ---------- LOGIN ----------
@app.route("/login", methods=["POST"])
def login():
    roll = request.form["roll"]
    password = request.form["password"]

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM students WHERE roll_number=?",
        (roll,)
    )

    user = cursor.fetchone()
    conn.close()

    if user is None:
        return render_template("login.html", error="Invalid Roll Number")

    if not check_password_hash(user["password"], password):
        return render_template("login.html", error="Invalid Password")

    session["user"] = roll
    return redirect(url_for("dashboard"))





# ---------- DASHBOARD ----------
@app.route("/dashboard")
def dashboard():
    if not is_logged_in():
        return redirect(url_for("home"))

    return render_template("dashboard.html", roll=session["user"])



#------------CHANGE PASSWORD ----------
@app.route("/change-password", methods=["GET", "POST"])
def change_password():
    if not is_logged_in():
        return redirect(url_for("home"))

    if request.method == "POST":
        old_password = request.form["old_password"]
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM students WHERE roll_number=?",
            (session["user"],)
        )
        user = cursor.fetchone()

        # Check old password
        if not check_password_hash(user["password"], old_password):
            conn.close()
            return render_template("change_password.html", error="Old password is incorrect")

        # Check new password match
        if new_password != confirm_password:
            conn.close()
            return render_template("change_password.html", error="Passwords do not match")

        # Update password
        hashed_password = generate_password_hash(new_password)

        cursor.execute(
            "UPDATE students SET password=? WHERE roll_number=?",
            (hashed_password, session["user"])
        )
        conn.commit()
        conn.close()

        return render_template("change_password.html", success="Password updated successfully")

    return render_template("change_password.html")  

@app.route('/courses')
def courses():
    return render_template("courses.html")

@app.route('/attendance')
def attendance():
    return render_template("attendance.html")

@app.route('/events')
def events():
    return render_template("events.html")

@app.route('/clubs')
def clubs():
    return render_template("clubs.html")

@app.route('/feedback')
def feedback():
    return render_template("feedback.html")

@app.route('/schedule')
def schedule():
    today = datetime.now().strftime("%A")

    if today == "Sunday":
        return render_template("schedule.html", holiday=True)

    classes = ["Math", "Physics", "DSA"]  # your subjects

    return render_template("schedule.html", holiday=False, classes=classes)
# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route('/test')
def test():
    return "TEST WORKING"
print("ALL ROUTES ENDING")
# ---------- RUN ----------
import os
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))