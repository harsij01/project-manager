from flask import Flask, render_template, request, flash, redirect, url_for, abort, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from sqlalchemy import or_
from models import db, User, Project, Task, ActivityLog
from helpers import admin_required
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import re
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == 'POST':
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash("Invalid email format", "error")
            return redirect(url_for("register"))

        if len(password) < 8:
            flash("Password must be at least 8 characters long.", "error")
            return redirect(url_for('register'))

        if not re.search(r"[A-Z]", password):
            flash("Password must contain at least one uppercase letter.", "error")
            return redirect(url_for('register'))

        if not re.search(r"[a-z]", password):
            flash("Password must contain at least one lowercase letter.", "error")
            return redirect(url_for('register'))

        if not re.search(r"[0-9]", password):
            flash("Password must contain at least one number.", "error")
            return redirect(url_for('register'))

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

        log = ActivityLog(
            action=f"Project '{name}' was created",
            user=current_user,
            project=new_project
        )
        db.session.add(log)
        db.session.commit()

        flash("Project created successfully!", "success")
        return redirect(url_for("dashboard"))

    return render_template('create_project.html')

@app.route('/projects/<int:id>')
@login_required
def project_details(id):
    project = Project.query.get_or_404(id)

    if current_user.role != "admin" and current_user not in project.members:
        abort(403)

    # Get filter values from URL
    priority = request.args.get("priority")
    status = request.args.get("status")
    search = request.args.get("search")
    assigned_user = request.args.get("assigned_user")

     # Base query
    query = Task.query.filter_by(project_id=id)

    if priority:
        query = query.filter(Task.priority == priority)

    if status:
        query = query.filter(Task.status == status)

    if search:
        query = query.filter(Task.name.ilike(f"%{search}%"))

    if assigned_user:
        query = query.join(Task.assignees).filter(User.id == assigned_user)


    filtered_tasks = query.all()

    # Split into Kanban columns
    todo_tasks = [t for t in filtered_tasks if t.status == "To Do"]
    inprogress_tasks = [t for t in filtered_tasks if t.status == "In Progress"]
    done_tasks = [t for t in filtered_tasks if t.status == "Done"]

    users = project.members

    return render_template(
        "project_details.html",
        project=project,
        users=users,
        todo_tasks=todo_tasks,
        inprogress_tasks=inprogress_tasks,
        done_tasks=done_tasks
    )

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
            project=project,
            status="To Do"
        )

        user_ids = request.form.getlist("assignees")
        for user_id in user_ids:
            user = User.query.get(user_id)
            if user and user in project.members:
                task.assignees.append(user)

        db.session.add(task)
        db.session.commit()

        log = ActivityLog(
            action=f"Task '{task.name}' was created",
            user=current_user,
            project=project
        )
        db.session.add(log)
        db.session.commit()

        return redirect(url_for("project_details", id=id))
    
    members = project.members
    return render_template("create_task.html", project=project, members=members)

@app.route('/tasks/<int:id>/update_status', methods=["POST"])
@login_required
def update_task(id):
    task = Task.query.get_or_404(id)

    if current_user.role != "admin" and current_user not in task.project.members:
        return jsonify(success=False), 403

    data = request.get_json()
    if not data or "status" not in data:
        return jsonify(success=False), 400

    new_status = data["status"]

    if new_status == "Done":
        task.completed_at = datetime.utcnow()

    if new_status in Task.ALLOWED_STATUSES:
        old_status = task.status   # save BEFORE changing

        if old_status != new_status:
            task.status = new_status

            log = ActivityLog(
                action=f"Task '{task.name}' moved from {old_status} to {new_status}",
                user=current_user,
                project=task.project
            )

            db.session.add(log)
            db.session.commit()

        return jsonify(success=True)

    return jsonify(success=False), 400

@app.route('/projects/<int:id>/timeline')
@login_required
def project_timeline(id):
    project = Project.query.get_or_404(id)

    if current_user.role != "admin" and current_user not in project.members:
        abort(403)

    logs = ActivityLog.query.filter_by(project_id=id)\
                .order_by(ActivityLog.timestamp.desc())\
                .all()

    return render_template("project_timeline.html", project=project, logs=logs)

@app.route('/projects/<int:id>/analytics')
@login_required
def project_analytics(id):
    project = Project.query.get_or_404(id)

    if current_user.role != "admin" and current_user not in project.members:
        abort(403)

    tasks = project.tasks

    # Completed tasks per user
    completed_tasks = Task.query.filter_by(project_id=id, status="Done").all()

    completed_per_user = {}
    for task in completed_tasks:
        for user in task.assignees:
            completed_per_user[user.name] = completed_per_user.get(user.name, 0) + 1

    # Overdue tasks
    overdue_count = len([
        t for t in tasks
        if t.deadline and t.status.lower() != "done" and datetime.utcnow() > t.deadline
    ])

    # High priority tasks
    high_priority_count = len([
        t for t in tasks if t.priority and t.priority.lower() == "high"
    ])

    # Average completion time (in days)
    completion_times = []
    for task in completed_tasks:
        if task.created_at and task.completed_at:
            delta = task.completed_at - task.created_at
            completion_times.append(delta.days)

    avg_completion_time = round(
        sum(completion_times) / len(completion_times), 2
    ) if completion_times else 0

    return render_template(
        "project_analytics.html",
        project=project,
        completed_per_user=completed_per_user,
        overdue_count=overdue_count,
        high_priority_count=high_priority_count,
        avg_completion_time=avg_completion_time
    )

if __name__ == "__main__":
    app.run(debug=True)
