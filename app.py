from flask import Flask, render_template, request, flash, redirect, url_for, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from functools import wraps
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'default_developement_key'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

project_members = db.Table(
    "project_members",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
    db.Column("project_id", db.Integer, db.ForeignKey("project.id"))
)

task_assignees = db.Table(
    "task_assignees",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
    db.Column("task_id", db.Integer, db.ForeignKey("task.id"))
)

class User(UserMixin, db.Model):
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

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)

    priority = db.Column(db.String(50))
    status = db.Column(db.String(50), default="Pending")

    deadline = db.Column(db.DateTime)

    project_id = db.Column(db.Integer, db.ForeignKey("project.id"))
    project = db.relationship("Project", backref="tasks")

    assignees = db.relationship(
        "User",
        secondary=task_assignees,
        backref="tasks"
    )

    @property
    def display_status(self):
        if self.deadline and self.status != "Completed":
            if datetime.utcnow() > self.deadline:
                return "Overdue"
        return self.status

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
        return redirect(url_for('login'))

    return render_template('register.html')
    
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != "admin":
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            if user and check_password_hash(user.password_hash, password):
                login_user(user)
                flash("Login successful!")
                return redirect(url_for('dashboard'))
        else:
            flash("Incorrect email or password")
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully!")
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

        new_project = Project(
            name=name,
            description=description,
            created_by=current_user.id
        )

        db.session.add(new_project)
        db.session.commit()

        flash("Project created successfully!")
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

    return render_template("project_details.html", project=project)

@app.route('/projects/<id>/add_member', methods=["POST"])
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

@app.route('/projects/<int:id>/create_task', methods=["GET", "POST"])
@login_required
@admin_required
def create_task(id):
    project = Project.query.get_or_404(id)

    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        priority = request.form.get("priority")
        deadline = request.form.get("deadline")

        task = Task(
            name=name,
            description=description,
            priority=priority,
            deadline=datetime.strptime(deadline, "%Y-%m-%d"),
            project=project
        )

        user_ids = request.form.getlist("assignees")
        for user_id in user_ids:
            user = User.query.get(user_id)
            task.assignees.append(user)

        db.session.add(task)
        db.session.commit()

        return redirect(url_for("project_detail", id=id))
    
    members = project.members
    return render_template("create_task.html", project=project, members=members)

@app.route('/projects/<int:id>/update_task', methods=["POST"])
@login_required
@admin_required
def update_task():
    task = Task.query.get_or_404(id)

    if current_user not in task.assignees:
        abort(403)

    new_status = request.form.get("status")
    task.status = new_status

    db.session.commit()

    return redirect(url_for("project_detail", id=task.project_id))

if __name__ == "__main__":
    app.run(debug=True)
