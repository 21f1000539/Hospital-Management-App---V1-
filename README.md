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
└── README.md          # Project documentation
```

## Milestones

### Milestone 1: Database Models and Schema Setup ✅
- Created database models for Admin, Doctor, Patient, Department, Appointment, and Treatment
- Defined relationships between tables
- Programmatic database creation
- Predefined Admin user creation
