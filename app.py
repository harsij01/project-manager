from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
import sqlite3

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    role = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(300), nullable=False)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    description = db.Column(db.String(300))
    status = db.Column(db.String(20), nullable=False, default="active")

@app.route('/')
def home():
    return render_template('layout.html')

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == 'POST':
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        password_hash = generate_password_hash(password)

        conn = sqlite3.connect("instance/database.db")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username = ? OR email = ?", (username, email))
        existing_user = cursor.fetchone()

        if existing_user:
            flash("Username or Email already exists")
            return redirect(url_for('register'))
        
        cursor.execute("INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)", (username, email, password_hash))

        conn.commit()
        conn.close()

        flash("Registration Successful")
        redirect(url_for('login'))

    return render_template('register.html')

@app.route('/project')
def project():
    return render_template('project.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/kanban')
def kanban():
    return render_template('kanban.html')

if __name__ == "__main__":
    app.run(debug=True)
