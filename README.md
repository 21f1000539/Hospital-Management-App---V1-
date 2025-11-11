# Hospital Management System

A comprehensive web application for managing hospital operations, built with Flask, SQLite, and Bootstrap.

## Features

- **Admin Dashboard**: Manage doctors, patients, and appointments
- **Doctor Portal**: View appointments, update patient treatments, manage availability
- **Patient Portal**: Book appointments, view medical history, search doctors

## Tech Stack

- **Backend**: Flask
- **Frontend**: HTML, CSS, Bootstrap, Jinja2
- **Database**: SQLite (programmatically created)

## Setup Instructions

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Initialize the database:
```bash
python init_db.py
```

3. Run the application:
```bash
python app.py
```

4. Access the application at `http://localhost:5000`

## Default Admin Credentials

- Username: `admin`
- Password: `admin123`

## Project Structure

```
Hospital-Management-App---V1-/
├── app.py              # Main Flask application
├── database.py         # Database initialization
├── models.py           # Database models
├── init_db.py          # Database setup script
├── requirements.txt    # Python dependencies
├── templates/          # Jinja2 templates
│   ├── base.html       # Base template
│   ├── login.html      # Login page
│   ├── register.html   # Patient registration
│   ├── admin/          # Admin templates
│   ├── doctor/         # Doctor templates
│   └── patient/        # Patient templates
├── static/             # Static files (CSS, JS)
└── README.md          # Project documentation
```

## Milestones

### Milestone 1: Database Models and Schema Setup ✅
- Created database models for Admin, Doctor, Patient, Department, Appointment, and Treatment
- Defined relationships between tables
- Programmatic database creation
- Predefined Admin user creation

### Milestone 2: Authentication and Role-Based Access ✅
- Implemented Patient registration and login
- Created Doctor and Admin login (Admin is predefined, no registration allowed)
- Admin will add Doctor's Details, Doctors cannot register by themselves
- Redirect users to role-specific dashboards after login (Admin, Doctor, Patient)
- Session-based authentication with role-based access control
- Bootstrap-styled login and registration pages
- Role-specific dashboard templates

### Milestone 3: Admin Dashboard and Management ✅
- Dashboard showing total doctors, patients, and appointments with statistics
- Add and update doctor profiles (name, specialization, department, availability)
- View all appointments (upcoming and past) with filtering by status and date
- Search patients by name, ID, email, or contact information
- Search doctors by name, specialization, or ID
- Blacklist/remove doctors and patients from the system
- Department management (add, view departments)
- Patient management (view, edit, blacklist/activate patients)
- Complete admin navigation in navbar
