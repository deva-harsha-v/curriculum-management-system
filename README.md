# 🎓 Curriculum Management System

A role-based Curriculum Management System built using **Python** and **Django** to streamline academic curriculum planning and management for educational institutions. The system enables administrators, Heads of Department (HODs), and faculty members to collaboratively manage curriculum versions, course outcomes, program outcomes, graduate attributes, and departmental information through a secure workflow.

---

## 📖 Overview

Managing academic curricula across departments can be complex and time-consuming. This application digitizes the entire curriculum management process by providing role-based access, structured data management, curriculum versioning, and automated PDF report generation.

The project follows Django's MVC architecture and demonstrates backend concepts such as authentication, authorization, relational database design, business logic implementation, and server-side rendering.

---

## ✨ Features

### 👤 User Management
- Secure user authentication
- Role-based authorization
- Admin, HOD, and Faculty dashboards
- Department-level access control

### 📚 Curriculum Management
- Create and manage curriculum versions
- Manage departments
- Course management
- Subject management
- Academic regulation support

### 🎯 Outcome Management
- Course Outcomes (CO)
- Program Outcomes (PO)
- Program Educational Objectives (PEO)
- Graduate Attributes (GA)

### 📄 Reports
- PDF generation using ReportLab
- Curriculum report export
- Printable academic documents

### 🔒 Security
- Authentication & session management
- Role-based permissions
- Protected routes
- Department-specific authorization

---

# 🛠️ Tech Stack

## Backend
- Python
- Django

## Database
- SQLite

## Frontend
- HTML
- CSS
- JavaScript
- Bootstrap

## Libraries
- ReportLab
- Graphviz
- Pillow
- Python Decouple
- WhiteNoise

---

# 📂 Project Structure

```
Curriculum Management System
│
├── accounts/
├── core/
├── curriculum/
├── pdf_generator/
├── static/
├── templates/
├── media/
├── manage.py
└── requirements.txt
```

---

# 🚀 Installation

Clone the repository

```bash
git clone https://github.com/deva-harsha-v/curriculum-management-system.git
```

Navigate to the project

```bash
cd curriculum-management-system
```

Create a virtual environment

```bash
python -m venv venv
```

Activate the environment

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run migrations

```bash
python manage.py migrate
```

Start the development server

```bash
python manage.py runserver
```

---

# 💡 Key Backend Concepts Demonstrated

- Django Project Architecture
- Authentication & Authorization
- Role-Based Access Control (RBAC)
- Relational Database Design
- Object-Oriented Programming
- Business Logic Implementation
- PDF Report Generation
- Form Validation
- Server-Side Rendering
- Session Management
- Department-Level Data Isolation

---

# 📸 Screenshots

> Add screenshots of:

- Login Page
- Dashboard
- Curriculum Management
- Course Management
- PDF Generation
- Faculty Dashboard

---

# 🔮 Future Improvements

- REST APIs using Django REST Framework
- FastAPI microservices
- PostgreSQL support
- Docker containerization
- Email notifications
- Cloud deployment (AWS/Azure)
- CI/CD pipeline
- Unit & Integration Testing

---

# 👨‍💻 Author

**Deva Harsha V**

- GitHub: https://github.com/deva-harsha-v
- LinkedIn: https://www.linkedin.com/in/deva-harsha-v/

---

# 📄 License

This project is licensed under the MIT License.

---

## ⭐ If you found this project useful, consider giving it a star!
