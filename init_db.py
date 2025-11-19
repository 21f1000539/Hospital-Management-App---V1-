"""
Unified database initialization / fix script

This script combines the functionality of the original `init_db.py` (initial database creation) and
`fix_database.py` (drop‑and‑recreate with schema verification). It can be invoked with a
command‑line argument to choose the desired mode:

    python init_db.py init   # create tables if they don't exist (drops existing tables first)
    python init_db.py fix    # drop all tables, recreate them, and verify the schema

Both modes ensure that the predefined admin user (`admin` / `admin123`) exists.
"""

import sys
from app import app
from database import db
from models import Admin, Doctor, Patient, Department, Appointment, Treatment, DoctorAvailability
from werkzeug.security import generate_password_hash


def _create_admin():
    """Create the predefined admin user if it does not already exist."""
    admin = Admin.query.filter_by(username="admin").first()
    if not admin:
        admin = Admin(
            username="admin",
            password=generate_password_hash("admin123"),
            email="admin@hospital.com",
            name="Hospital Administrator",
        )
        db.session.add(admin)
        db.session.commit()
        print("[SUCCESS] Predefined Admin user created successfully!")
        print("  Username: admin")
        print("  Password: admin123")
    else:
        print("[INFO] Admin user already exists!")


def init_database():
    """Initial setup – drop any existing tables, recreate the schema, and add the admin user.
    This mirrors the original `init_db.py` behaviour.
    """
    with app.app_context():
        # Drop all existing tables (useful for a fresh start)
        db.drop_all()
        # Create tables according to the current models
        db.create_all()
        print("[SUCCESS] Database tables created successfully!")
        _create_admin()
        print("\nDatabase initialization completed!")


def fix_database():
    """Fix / reset the database – drop all tables, recreate them, then verify the schema.
    This mirrors the original `fix_database.py` behaviour.
    """
    with app.app_context():
        print("Dropping all existing tables...")
        db.drop_all()
        print("Creating all tables with new schema...")
        db.create_all()
        print("[SUCCESS] Database tables created successfully!")
        _create_admin()

        # Verify that the expected columns are present (example: new Doctor fields)
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        doctor_columns = [col["name"] for col in inspector.get_columns("doctor")]
        print("\nDoctor table columns:", doctor_columns)
        # Adjust this check if you add/remove columns in the future
        required = {"qualifications", "experience"}
        if required.issubset(set(doctor_columns)):
            print("[SUCCESS] Database schema is correct!")
        else:
            missing = required - set(doctor_columns)
            print(f"[ERROR] Database schema is missing columns: {missing}")
        print("\nDatabase fix completed!")


if __name__ == "__main__":
    # Default to "init" if no argument is supplied for backward compatibility
    mode = sys.argv[1].lower() if len(sys.argv) > 1 else "init"
    if mode == "init":
        init_database()
    elif mode == "fix":
        fix_database()
    else:
        print("Usage: python init_db.py [init|fix]")
        sys.exit(1)
