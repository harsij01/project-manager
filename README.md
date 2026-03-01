# Enterprise Project Management System

A full-stack project management web application built with Flask, SQLAlchemy, and JavaScript, featuring Kanban task management, analytics dashboards, and secure authentication.

---

## Features
### Authentication & Security

- User registration and login
- Session-based authentication with Flask-Login
- CSRF protection using Flask-WTF
- Secure password hashing

### Project & Task Management

- Create and manage projects
- Assign tasks to users
- Set priorities and due dates
- Track task completion
- Status-based workflow (To Do / In Progress / Done)

### Kanban Board

- Drag-and-drop task movement
- Real-time status updates via fetch() API
- Visual workflow management

### Analytics Dashboard

- Interactive charts powered by Chart.js:
- Completed tasks per user (Bar chart)
- Overdue vs High priority tasks (Pie chart)
- Average completion time (Doughnut chart)

### Modern UI

- Responsive design
- Custom CSS with design variables
- Card-based layout
- Smooth hover animations
- Clean SaaS-inspired interface

---

## Tech Stack
Backend

- Flask
- Flask-SQLAlchemy
- Flask-Login
- Flask-WTF
- SQLite (development database)

Frontend

- HTML5
- CSS3 (custom styling system)
- Vanilla JavaScript
- Chart.js

---

## Installation & Setup

Clone the repository

```bash
git clone https://github.com/your-username/enterprise-project-management-system.git
cd enterprise-project-management-system
```

Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
```

Install dependencies

```bash
pip install -r requirements.txt
```

Set environment variables

```bash
export FLASK_APP=app.py      # Mac/Linux
set FLASK_APP=app.py         # Windows

export FLASK_ENV=development
```

Run the application

```bash
flask run
```

Visit:

```bash
http://127.0.0.1:5000/
```
---

## Security

- CSRF protection enabled
- Session-based authentication
- Secure form validation
- Protected POST routes

---

## Database Setup

This project uses **Flask** with **SQLAlchemy** for database management. Follow these steps to create and populate the database:

### 1. Create the Database Tables

Run the Python shell or a script to create the tables:

```bash
python3
```
Then in the Python shell:

```bash
from app import app, db

with app.app_context():
    db.create_all()
```
### 2. Create an Admin User

To create an admin user for your application, run the Python shell:

```bash
python3
```

Then in the Python shell:

```bash
from app import app, db
from models import User
from werkzeug.security import generate_password_hash

# Replace values in brackets with your own
admin = User(
    name="[Your Name]",
    email="[your-email@example.com]",
    password_hash=generate_password_hash("[your-password]"),
    role="admin"
)

with app.app_context():
    db.session.add(admin)
    db.session.commit()
```

---

## Screenshots

### Home page
![Home](screenshots/home.png)

### Dashboard
![Dashboard](screenshots/dashboard.png)

### Project Details
![Project Details](screenshots/project_details.png)

### Project Analytics
![Project Analytics](screenshots/project_analytics.png)

### Project Timeline
![Project Timeline](screenshots/project_timeline.png)