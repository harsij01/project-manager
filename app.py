from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from werkzeug.security import generate_password_hash, check_password_hash
import os
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'default_developement_key'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

project_members = db.Table(
    "project_members",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
    db.Column("project_id", db.Integer, db.ForeignKey("project.id"))
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    role = db.Column(db.String(20), nullable=False, default="member")
    password_hash = db.Column(db.String(300), nullable=False)

    projects = db.relationship(
        "Project",
        secondary=project_members,
        back_populates="members"
    )

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    description = db.Column(db.String(300))

    members = db.relationship(
        "User",
        secondary=project_members,
        back_populates="projects"
    )

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

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login first")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function
    
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_role") != "admin":
            flash("Admins only.")
            return redirect(url_for("dashboard"))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            session["user_id"] = user.id
            session["user_role"] = user.role
            flash("Login successful!")
            return redirect(url_for('dashboard'))
        else:
            flash("Incorrect email or password")
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("Log out successfully!")
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/admin_panel')
@login_required
@admin_required
def admin_panel():
    return render_template("admin_panel.html")

@app.route('/project/create', methods=["GET", "POST"])
@login_required
@admin_required
def create_project():
    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]

        new_project = Project(name=name, description=description, created_by=session["user_id"])

        db.session.add(new_project)
        db.session.commit()

        flash("Project created successfully!")
        return redirect(url_for("dashboard"))

    return render_template('create_project.html')

@app.route('/projects')
@login_required
def view_projects():
    projects = Project.query.all()
    return render_template("projects.html", projects=projects)

@app.route('/projects/<id>')
@login_required
def project_details(id):
    project = Project.query.get_or_404(id)
    return render_template("project_details.html", project=project)

@app.route('/projects/<id>/add-member', methods=["POST"])
@login_required
@admin_required
def add_member(id):
    project = Project.query.get_or_404(id)

    user_id = request.form.get("user_id")
    user = User.query.get(user_id)

    if user not in project.members:
        project.members.append(user)
        db.session.commit()

    return redirect(url_for("project_details", id=id))

@app.route('/kanban')
def kanban():
    return render_template('kanban.html')

if __name__ == "__main__":
    app.run(debug=True)
