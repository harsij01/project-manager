from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    members = db.relationship(
        "User",
        secondary=project_members,
        back_populates="projects"
    )

    @property
    def progress_percentage(self):
        total_tasks = len(self.tasks)
        if total_tasks == 0:
            return 0

        completed_tasks = len([task for task in self.tasks if task.status.strip().lower() == "done"])

        return round((completed_tasks / total_tasks) * 100)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

    priority = db.Column(db.String(50))
    status = db.Column(db.String(50), default="To Do", nullable=False)
    ALLOWED_STATUSES = ["To Do", "In Progress", "Done"]

    deadline = db.Column(db.DateTime)

    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), nullable=False)
    project = db.relationship(
        "Project",
        backref=db.backref("tasks", cascade="all, delete-orphan")
    )

    assignees = db.relationship(
        "User",
        secondary=task_assignees,
        backref="tasks"
    )

    @property
    def display_status(self):
        if self.deadline and self.status.lower() != "done":
            if datetime.utcnow() > self.deadline:
                return "Overdue"
        return self.status or "To Do"

class ActivityLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    action = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Who performed the action
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = db.relationship("User")

    # Which project it belongs to
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), nullable=False)
    project = db.relationship(
        "Project",
        backref=db.backref("activity_logs", cascade="all, delete-orphan")
    )