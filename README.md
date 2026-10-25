# 🎓 Curriculum Management System (CMS)

A production-ready, secure, role-based Curriculum Management System built using **Python 3.11** and **Django 4.2 LTS (Django==4.2.13)** to streamline academic curriculum planning, syllabus tracking, outcome-based education (OBE) mapping, and automated institutional PDF generation for engineering colleges and universities.

The system enforces strict multi-role governance (Administrator, Head of Department, and Faculty) with isolated departmental boundaries, a formal change-request approval workflow, immutable published curricula, and automated ReportLab PDF compilation with Graphviz prerequisite dependency visualization.

---

## 📋 Table of Contents
- [Architecture & Design](#-architecture--design)
- [Role-Based Access Control (RBAC)](#-role-based-access-control-rbac)
- [Key Features](#-key-features)
- [Outcome-Based Education (OBE) Matrix](#-outcome-based-education-obe-matrix)
- [Prerequisite Dependency Graph & Fallback](#-prerequisite-dependency-graph--fallback)
- [Automated Testing Suite (31 Tests)](#-automated-testing-suite-31-tests)
- [Local Development Setup](#-local-development-setup)
- [Environment Configuration](#-environment-configuration)
- [Production Deployment on PythonAnywhere](#-production-deployment-on-pythonanywhere)
- [ExcelR Internship Compliance Checklist](#-excelr-internship-compliance-checklist)
- [License & Author](#-license--author)

---

## 🏗️ Architecture & Design

The application follows Django's clean Model-View-Template (MVT) pattern, organized into modular apps with clear separation of concerns:

```
curriculum-management-system-main/
├── accounts/                  # User authentication, profiles, role management, activation
│   ├── models.py              # UserProfile with Role (ADMIN, HOD, FACULTY), Department FK
│   ├── views.py               # Login, POST-only Logout, Admin Dashboard, User Activation
│   ├── forms.py               # Custom User & Profile creation forms
│   └── tests.py               # 8 Automated RBAC & authentication tests
├── curriculum/                # Core curriculum data, OBE mappings, workflow engine
│   ├── models.py              # Department, CurriculumVersion, Course, PEO, PO, CO, AuditLog
│   ├── views.py               # Versions, Courses, Matrices, Change Requests, Approvals
│   ├── forms.py               # Forms with dynamic clean validation for matrices & courses
│   ├── templatetags/          # Custom filters (e.g., enhanced dict lookup get_item)
│   └── tests.py               # 15 Automated lifecycle, workflow, & isolation tests
├── pdf_generator/             # Official institutional curriculum book compiler
│   ├── generator.py           # ReportLab Platypus document template & flowable builder
│   ├── prereq_chart.py        # Graphviz directed dependency generator with fallback
│   ├── styles.py              # Typography, layout dimensions, palettes, & table styles
│   ├── views.py               # PDF preview, streaming, and direct download views
│   └── tests.py               # 8 Automated PDF compilation & fallback tests
├── core/                      # Project root configuration
│   ├── settings.py            # Security-hardened settings with decouple & WhiteNoise
│   ├── urls.py                # Top-level URL routing
│   ├── wsgi.py                # WSGI application entrypoint
│   └── context_processors.py  # Global context (e.g. INSTITUTION_NAME)
├── static/                    # Centralized CSS and JS assets
│   ├── css/app.css            # Responsive layout, audit highlights, diff styling
│   └── js/app.js              # Matrix validation, toasts, CSRF helpers, confirm modals
├── templates/                 # Server-side Bootstrap 5.3.3 templates
│   ├── base.html              # Responsive layout with role-aware navigation
│   ├── accounts/              # Authentication & user administration templates
│   ├── curriculum/            # Versioning, courses, matrices, change review screens
│   └── pdf_generator/         # Generation confirmation and preview modals
├── pythonanywhere_wsgi.py.template # Ready-to-use PythonAnywhere WSGI configuration
├── requirements.txt           # Production pinned dependencies
├── .env.example               # Environment variable specification
└── manage.py
```

---

## 🔐 Role-Based Access Control (RBAC)

The system implements strict horizontal and vertical access boundaries:

| Capability | Administrator | Head of Department (HOD) | Faculty Member |
| :--- | :---: | :---: | :---: |
| **Manage Users & Roles** | ✅ Full Access | ❌ Forbidden | ❌ Forbidden |
| **Toggle User Active Status** | ✅ Yes | ❌ Forbidden | ❌ Forbidden |
| **Create Curriculum Versions** | ✅ Any Department | ✅ Own Department Only | ❌ Forbidden |
| **Publish / Archive Versions** | ✅ Yes | ✅ Own Department Only | ❌ Forbidden |
| **Direct Course Edit (Draft)** | ✅ Yes | ✅ Own Department Only | ❌ Submitted as Change Request |
| **Review & Approve Changes** | ✅ Yes | ✅ Own Department Only | ❌ Forbidden |
| **View Audit Trail** | ✅ Global | ✅ Own Department Only | ❌ Forbidden |
| **Download PDF** | ✅ All Versions | ✅ All Versions (Own Dept) | ✅ Published Versions Only |
| **Cross-Department Access** | ✅ Permitted | ❌ 403 Forbidden | ❌ 403 Forbidden |

### Immutability & Workflow Guarantee
- Once a Curriculum Version moves to **PUBLISHED** status, direct editing of courses, syllabi, and outcome mappings is strictly blocked (`403 Forbidden`).
- When a Faculty member edits a course in a draft version, the change is saved as a **Change Request** with before/after state diffing. The HOD or Admin can inspect the side-by-side diff, provide comments, and approve or reject atomically with automatic rollback on error.
- All administrative actions (version creation, status transition, change approval, course deletion, PDF generation) generate structured records in `AuditLog`.

---

## ✨ Key Features

- **Automated Audit Logging**: Every critical lifecycle and curriculum event is captured with timestamp, user, action code, and detailed description.
- **CSRF-Protected Actions**: State-changing endpoints (including User Logout) enforce `POST` with CSRF validation.
- **Dynamic Matrix Mappings**:
  - Course Outcomes (CO) to Program Outcomes (PO) mapping with strength rating (`1=Low`, `2=Medium`, `3=High`).
  - Department Mission to Program Educational Objectives (PEO) mapping.
  - Program Educational Objectives (PEO) to Graduate Attributes (GA) mapping.
- **Security Hardening**:
  - `DEBUG=False` by default in production.
  - Configurable `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, and cookie security flags via `.env`.
  - WhiteNoise integration for high-performance static asset delivery with cache busting.
  - Institutional branding dynamically injected across all templates via context processors.

---

## 🎯 Outcome-Based Education (OBE) Matrix

The system fully supports the NBA/NAAC Outcome-Based Education framework:
1. **Vision & Mission**: Defined at both institute and departmental levels.
2. **Program Educational Objectives (PEO)**: Statements describing career and professional accomplishments.
3. **Graduate Attributes (GA)** & **Program Outcomes (PO)**: NBA 12 graduate attributes and department-specific outcomes.
4. **Course Outcomes (CO)**: Specific competencies achieved upon course completion.
5. **Correlation Matrices**: Intuitive web forms and matrix grids allowing faculty and HODs to map COs to POs/PSOs without manipulating raw JSON.

---

## 📊 Prerequisite Dependency Graph & Fallback

The PDF generator (`pdf_generator/prereq_chart.py`) constructs a directed acyclic graph (DAG) representing semester-by-semester course prerequisites:
- **Visual Graph**: Clusters courses by semester and connects dependencies via directed edges using Graphviz (`dot`).
- **Resilient Fallback**: If the deployment platform lacks Graphviz system binaries (such as PythonAnywhere free tier), the system gracefully catches `GraphvizExecutableNotFound` or OS execution errors, logs an informative warning, and automatically renders a cleanly formatted ReportLab dependency table into the PDF book instead of failing.

---

## 🧪 Automated Testing Suite (31 Tests)

The project includes an automated test suite with **31 unit, security, RBAC, and integration tests** across all apps.

```bash
# Run the complete test suite
python manage.py test

# Run tests by application
python manage.py test accounts
python manage.py test curriculum
python manage.py test pdf_generator
```

### Test Coverage Breakdown:
- **`accounts` (8 tests)**:
  - Valid user login and session creation
  - Rejection of invalid credentials
  - Inactive user login denial
  - POST-only logout protection (GET requests safely redirect with warning)
  - Role-based login redirection (Admin -> Admin Dashboard, HOD/Faculty -> Curriculum List)
  - Admin dashboard access control (non-admin receives 403 Forbidden)
  - Admin user activation/deactivation toggle
  - Department isolation on user management
- **`curriculum` (15 tests)**:
  - HOD draft version creation (auto-assigned to HOD's department)
  - Admin version creation with department selection
  - Version lifecycle transition (DRAFT -> PUBLISHED -> ARCHIVED)
  - Strict immutability of published curriculum versions
  - Cross-department isolation (HOD accessing other department receives 403)
  - HOD direct course creation and display ordering
  - Faculty course creation submitting a pending Change Request
  - Course prerequisite assignment and bidirectional deletion
  - CO-PO mapping numeric score validation (0-3)
  - Mission-PEO matrix mapping persistence
  - Atomic change request approval applying modifications to course
  - Atomic change request rejection leaving original course intact
  - Audit log recording and rollback protection
- **`pdf_generator` (8 tests)**:
  - Generate confirmation screen rendering with version metadata
  - HOD draft PDF preview permissions
  - Faculty draft PDF preview denial (403 Forbidden)
  - Faculty published PDF preview permission
  - Full ReportLab PDF compilation without course prerequisites
  - Full ReportLab PDF compilation with course prerequisites
  - Inline PDF streaming endpoint (`application/pdf`)
  - Graphviz failure fallback to structured dependency table

---

## 💻 Local Development Setup

### 1. Prerequisites
- Python 3.10, 3.11, or 3.12
- Git
- (Optional) Graphviz installed and added to system `PATH` for graphical prerequisite diagrams

### 2. Clone and Setup Environment
```bash
# Clone repository
git clone https://github.com/deva-harsha-v/curriculum-management-system.git
cd curriculum-management-system

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Windows (cmd):
.venv\Scripts\activate.bat
# Linux / macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables
```bash
# Copy example configuration
cp .env.example .env
```
Edit `.env` for local development:
```ini
DEBUG=True
SECRET_KEY=local-dev-secret-key-change-in-production-1234567890
ALLOWED_HOSTS=127.0.0.1,localhost
CSRF_TRUSTED_ORIGINS=http://127.0.0.1,http://localhost
INSTITUTION_NAME=ABC Institute of Technology
```

### 4. Database Setup & Static Assets
```bash
# Apply migrations
python manage.py migrate

# Collect static assets
python manage.py collectstatic --noinput

# Verify automated test suite
python manage.py test
```

### 5. Create Superuser & Run Server
```bash
# Create administrator account
python manage.py createsuperuser

# Start development server
python manage.py runserver
```
Visit `http://127.0.0.1:8000/` in your browser.

---

## ⚙️ Environment Configuration

| Variable | Description | Default / Example |
| :--- | :--- | :--- |
| `DEBUG` | Enable debug mode (Must be `False` in production) | `False` |
| `SECRET_KEY` | Cryptographic secret for signing sessions & tokens | 50+ character random string |
| `ALLOWED_HOSTS` | Comma-separated allowed hostnames | `127.0.0.1,localhost,yourname.pythonanywhere.com` |
| `CSRF_TRUSTED_ORIGINS` | Comma-separated trusted origin URLs | `https://yourname.pythonanywhere.com` |
| `INSTITUTION_NAME` | Global institution name displayed on navbar & PDF | `Curriculum Management System` |
| `SECURE_SSL_REDIRECT` | Redirect HTTP requests to HTTPS in production | `False` (Set `True` on SSL domains) |
| `SESSION_COOKIE_SECURE`| Send session cookie only over HTTPS | `False` (Set `True` on SSL domains) |
| `CSRF_COOKIE_SECURE` | Send CSRF cookie only over HTTPS | `False` (Set `True` on SSL domains) |
| `DJANGO_LOG_LEVEL` | Logging verbosity | `INFO` |

---

## ☁️ Production Deployment on PythonAnywhere

Follow these steps to deploy this repository to PythonAnywhere:

### Step 1: Clone Repository on PythonAnywhere
Open a **Bash Console** in your PythonAnywhere dashboard:
```bash
git clone https://github.com/deva-harsha-v/curriculum-management-system.git
cd curriculum-management-system
```

### Step 2: Create and Configure Virtualenv
```bash
# Create virtual environment with Python 3.11
mkvirtualenv --python=/usr/bin/python3.11 cms-env

# Install requirements
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables
```bash
cp .env.example .env
nano .env
```
Set the following values in `.env`:
```ini
DEBUG=False
SECRET_KEY=generate-a-strong-random-key-here-with-at-least-50-characters
ALLOWED_HOSTS=yourusername.pythonanywhere.com
CSRF_TRUSTED_ORIGINS=https://yourusername.pythonanywhere.com
INSTITUTION_NAME=Department of Computer Science & Engineering
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### Step 4: Run Migrations and Collect Static Files
```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

### Step 5: Configure the Web Tab
1. Navigate to the **Web** tab in PythonAnywhere.
2. Click **Add a new web app**, choose **Manual configuration**, and select **Python 3.11**.
3. Under **Virtualenv**, set the path to your virtualenv:
   `/home/yourusername/.virtualenvs/cms-env`
4. Under **Static files**, configure static and media mappings:
   - **URL**: `/static/` ➔ **Directory**: `/home/yourusername/curriculum-management-system/staticfiles`
   - **URL**: `/media/` ➔ **Directory**: `/home/yourusername/curriculum-management-system/media`

### Step 6: Configure the WSGI File
Click on the **WSGI configuration file** link (`/var/www/yourusername_pythonanywhere_com_wsgi.py`). Replace its contents with:

```python
import os
import sys

# Project directory
project_home = '/home/yourusername/curriculum-management-system'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Load environment variables from .env
env_path = os.path.join(project_home, '.env')
if os.path.exists(env_path):
    try:
        from dotenv import load_dotenv
        load_dotenv(env_path)
    except ImportError:
        pass

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### Step 7: Reload Web App
Click the green **Reload yourusername.pythonanywhere.com** button at the top of the Web tab. Your application is live!

---

## 📑 ExcelR Internship Compliance Checklist

This project has been verified against all evaluation criteria:

| Requirement | Implementation & Location | Status |
| :--- | :--- | :---: |
| **Role-Based Access Control** | Admin, HOD, and Faculty roles with profile assignment (`accounts/models.py`, `accounts/views.py`) | ✅ Compliant |
| **Department Isolation** | `@dept_required` decorator, `get_version_or_403` preventing cross-department access (`curriculum/views.py`) | ✅ Compliant |
| **Curriculum Lifecycle** | DRAFT, PUBLISHED, ARCHIVED states with published immutability protection (`curriculum/models.py`) | ✅ Compliant |
| **Change Request Workflow** | Faculty edits trigger approval queue; HOD reviews side-by-side diffs atomically (`curriculum/views.py`) | ✅ Compliant |
| **OBE Outcomes & Matrices** | CO, PO, PEO, GA models with matrix validation forms and dynamic UI (`curriculum/forms.py`, `templates/`) | ✅ Compliant |
| **Audit Trail** | Structured `AuditLog` model recording user, department, timestamp, and actions (`curriculum/models.py`) | ✅ Compliant |
| **Automated PDF Export** | Comprehensive institutional syllabus book generated using ReportLab (`pdf_generator/generator.py`) | ✅ Compliant |
| **Prerequisite DAG / Fallback** | Graphviz dependency graph with automatic table fallback for zero-dependency hosting (`pdf_generator/`) | ✅ Compliant |
| **Security Standards** | CSRF tokens on all POST forms, POST-only logout, password toggles, no hardcoded secrets (`core/settings.py`) | ✅ Compliant |
| **Static & Styling** | Centralized `static/css/app.css` and `static/js/app.js`, WhiteNoise static post-processing | ✅ Compliant |
| **Automated Testing** | 31 comprehensive unit, integration, and security tests passing with zero failures (`manage.py test`) | ✅ Compliant |
| **Production Ready** | `check --deploy` verified, `.env.example`, PythonAnywhere WSGI template and deployment guide | ✅ Compliant |

---

## 👨‍💻 Author

**Deva Harsha V**
- GitHub: [deva-harsha-v](https://github.com/deva-harsha-v)
- LinkedIn: [deva-harsha-v](https://www.linkedin.com/in/deva-harsha-v/)

---

## 📄 License

This project is licensed under the MIT License — see the LICENSE file for details.
