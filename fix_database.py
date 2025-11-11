"""
Script to fix database schema by dropping and recreating all tables
"""
from app import app
from database import db
from models import Admin, Doctor, Patient, Department, Appointment, Treatment, DoctorAvailability
from werkzeug.security import generate_password_hash

def fix_database():
    """Drop all tables and recreate with new schema"""
    with app.app_context():
        print("Dropping all existing tables...")
        db.drop_all()
        print("Creating all tables with new schema...")
        db.create_all()
        print("[SUCCESS] Database tables created successfully!")
        
        # Create predefined Admin user
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
        
        # Verify schema
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        doctor_columns = [col['name'] for col in inspector.get_columns('doctor')]
        print("\nDoctor table columns:", doctor_columns)
        
        if 'qualifications' in doctor_columns and 'experience' in doctor_columns:
            print("[SUCCESS] Database schema is correct!")
        else:
            print("[ERROR] Database schema is missing new columns!")
        
        print("\nDatabase fix completed!")

if __name__ == '__main__':
    fix_database()

