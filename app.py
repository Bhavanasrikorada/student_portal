from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# ---------------- DATABASE ----------------

def get_db():
    return sqlite3.connect("database.db")

def create_table():
    conn = get_db()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            email TEXT,
            password TEXT
        )
    """)

    # Feedback table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            course TEXT,
            faculty TEXT,
            message TEXT
        )
    """)

    conn.commit()
    conn.close()

# Call once when app starts
create_table()

# ---------------- AUTH ROUTES ----------------

@app.route('/')
def login():
    return render_template("login.html")

@app.route('/register')
def register():
    return render_template("register.html")

@app.route('/register_user', methods=['POST'])
def register_user():
    student_id = request.form['student_id'].strip()
    email = request.form['email'].strip()
    password = request.form['password'].strip()

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO users (student_id, email, password) VALUES (?, ?, ?)",
        (student_id, email, password)
    )

    conn.commit()
    conn.close()

    return redirect('/')

# ---------------- DASHBOARD ----------------

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():

    # When coming from login form
    if request.method == 'POST':
        login_id = request.form.get('login_id')
        password = request.form.get('password')

        if not login_id or not password:
            return "Invalid access. Please login first."

        login_id = login_id.strip()
        password = password.strip()

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE (email=? OR student_id=?) AND password=?",
            (login_id, login_id, password)
        )

        user = cursor.fetchone()
        conn.close()

        if user:
            return render_template("dashboard.html", student_id=login_id)
        else:
            return "Invalid credentials"

    # When clicking Home
    return render_template("dashboard.html", student_id="Student")

# ---------------- NAVIGATION PAGES ----------------

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

# ---------------- FEEDBACK ----------------

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        student_id = "demo"
        course = request.form['course']
        faculty = request.form['faculty']
        message = request.form['message']

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO feedback (student_id, course, faculty, message) VALUES (?, ?, ?, ?)",
            (student_id, course, faculty, message)
        )

        conn.commit()
        conn.close()

        return "Feedback submitted successfully!"

    return render_template("feedback.html")

# ---------------- SCHEDULE ----------------

from datetime import datetime

@app.route('/schedule')
def schedule():
    today = datetime.now().strftime("%A")

    schedule_data = {
        "Monday": ["Data Structures", "DBMS"],
        "Tuesday": ["Operating Systems", "Computer Networks"],
        "Wednesday": ["Machine Learning"],
        "Thursday": ["Cyber Security"],
        "Friday": ["Software Engineering"]
    }

    holidays = ["Sunday"]

    if today in holidays:
        return render_template("schedule.html", holiday=True, day=today)
    else:
        return render_template(
            "schedule.html",
            holiday=False,
            day=today,
            classes=schedule_data.get(today, [])
        )
# ---------------- RUN ----------------


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)