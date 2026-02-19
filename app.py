from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

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

app.route('/register', methods=["GET", "POST"])
def register():
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
