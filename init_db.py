"""
Database initialization script
This script creates all database tables programmatically and creates the predefined admin user.
"""
from app import app
from database import db
from models import Admin, Doctor, Patient, Department, Appointment, Treatment, DoctorAvailability
from werkzeug.security import generate_password_hash

def init_database():
    """Initialize database with tables and predefined admin user"""
    with app.app_context():
        # Create all tables
        db.create_all()
        print("[SUCCESS] Database tables created successfully!")
        
        # Create predefined Admin user if it doesn't exist
        admin = Admin.query.filter_by(username='admin').first()
        if not admin:
            admin = Admin(
                username='admin',
                password=generate_password_hash('admin123'),
                email='admin@hospital.com',
                name='Hospital Administrator'
            )
            db.session.add(admin)
            db.session.commit()
            print("[SUCCESS] Predefined Admin user created successfully!")
            print("  Username: admin")
            print("  Password: admin123")
        else:
            print("[INFO] Admin user already exists!")
        
        print("\nDatabase initialization completed!")

if __name__ == '__main__':
    init_database()

