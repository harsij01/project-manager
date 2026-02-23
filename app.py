from flask import Flask, render_template, request, flash, redirect, url_for, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Project, Task
from helpers import admin_required
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'default_development_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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
            flash("Username or Email already exists", "error")
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

        flash("Registration Successful", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Incorrect email or password", "error")
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully!", "success")
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == "admin":
        projects = Project.query.all()
    else:
        projects = current_user.projects

    return render_template("dashboard.html", projects=projects)

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

        new_project = Project(
            name=name,
            description=description,
            created_by=current_user.id
        )

        new_project.members.append(current_user)

        db.session.add(new_project)
        db.session.commit()

        flash("Project created successfully!", "success")
        return redirect(url_for("dashboard"))

    return render_template('create_project.html')

@app.route('/projects')
@login_required
def view_projects():
    if current_user.role == "admin":
        projects = Project.query.all()
    else:
        projects = current_user.projects
    return render_template("projects.html", projects=projects)

@app.route('/projects/<int:id>')
@login_required
def project_details(id):
    project = Project.query.get_or_404(id)

    if current_user.role != "admin" and current_user not in project.members:
        abort(403)

    users = User.query.all()
    return render_template("project_details.html", project=project, users=users)

@app.route('/projects/<int:id>/add_member', methods=["POST"])
@login_required
@admin_required
def add_member(id):
    project = Project.query.get_or_404(id)

    user_id = request.form.get("user_id")
    user = User.query.get_or_404(user_id)

    if user not in project.members:
        project.members.append(user)
        db.session.commit()

    return redirect(url_for("project_details", id=id))

@app.route('/projects/<int:id>/create_task', methods=["GET", "POST"])
@login_required
@admin_required
def create_task(id):
    project = Project.query.get_or_404(id)

    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        priority = request.form.get("priority")

        deadline_str = request.form.get("deadline")
        deadline = None

        if deadline_str:
            deadline = datetime.strptime(deadline_str, "%Y-%m-%d")

        task = Task(
            name=name,
            description=description,
            priority=priority,
            deadline=deadline,
            project=project
        )

        user_ids = request.form.getlist("assignees")
        for user_id in user_ids:
            user = User.query.get(user_id)
            if user and user in project.members:
                task.assignees.append(user)

        db.session.add(task)
        db.session.commit()

        return redirect(url_for("project_details", id=id))
    
    members = project.members
    return render_template("create_task.html", project=project, members=members)

@app.route('/tasks/<int:id>/update_status', methods=["POST"])
@login_required
def update_task(id):
    task = Task.query.get_or_404(id)

    if current_user.role != "admin" and current_user not in task.assignees:
        abort(403)

    task.status = request.form.get("status")
    db.session.commit()

    return redirect(url_for("project_details", id=task.project_id))

if __name__ == "__main__":
    app.run(debug=True)
