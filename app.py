from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'default_developement_key'

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

        existing_user = User.query.filter_by(name=username).first()
        existing_email = User.query.filter_by(email=email).first()

        if existing_user or existing_email:
            flash("Username or Email already exists")
            return redirect(url_for('register'))

        password_hash = generate_password_hash(password)

        new_user = User(
            name=username,
            email=email,
            role="member",
            password_hash=password_hash
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Registration Successful")
        redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        existing_user = User.query.filter_by(email=email).first()
        
        if existing_user and check_password_hash(existing_user.password_hash, password):
            flash("Login successful!")
            return redirect(url_for('dashboard'))
        else:
            flash("Incorrect email or password")
            return redirect(url_for('login'))

    return render_template('login.html')

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
