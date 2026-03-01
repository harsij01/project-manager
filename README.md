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