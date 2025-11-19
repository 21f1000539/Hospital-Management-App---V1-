from database import db
from datetime import datetime
from flask_login import UserMixin

class Admin(UserMixin, db.Model):
    """Admin model for hospital staff"""
    __tablename__ = 'admin'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Admin {self.username}>'

class Department(db.Model):
    """Department/Specialization model"""
    __tablename__ = 'department'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with Doctor
    doctors = db.relationship('Doctor', backref='department', lazy=True)
    
    def __repr__(self):
        return f'<Department {self.name}>'

class Doctor(UserMixin, db.Model):
    """Doctor model"""
    __tablename__ = 'doctor'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    specialization = db.Column(db.String(100), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=True)
    qualifications = db.Column(db.String(200))  # e.g., "MBBS, DM - Medical Oncology"
    experience = db.Column(db.Integer)  # Years of experience
    profile_description = db.Column(db.Text)  # Doctor profile description
    availability = db.Column(db.String(500))  # JSON string for availability schedule
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    appointments = db.relationship('Appointment', backref='doctor', lazy=True)
    availability_slots = db.relationship('DoctorAvailability', backref='doctor', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Doctor {self.name}>'

class Patient(UserMixin, db.Model):
    """Patient model"""
    __tablename__ = 'patient'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(10))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    appointments = db.relationship('Appointment', backref='patient', lazy=True)
    
    def __repr__(self):
        return f'<Patient {self.name}>'

class Appointment(db.Model):
    """Appointment model"""
    __tablename__ = 'appointment'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), default='Booked', nullable=False)  # Booked, Completed, Cancelled
    reason = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Note: Double booking prevention is handled in application logic
    # Application should check for existing 'Booked' appointments before creating new ones
    # Cancelled appointments free up the time slot for new bookings
    
    # Relationship with Treatment
    treatment = db.relationship('Treatment', backref='appointment', uselist=False, lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Appointment {self.id} - {self.date} {self.time}>'

class Treatment(db.Model):
    """Treatment model"""
    __tablename__ = 'treatment'
    
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'), unique=True, nullable=False)
    visit_type = db.Column(db.String(50))  # In-person, Teleconsultation, Follow-up, etc.
    test_done = db.Column(db.Text)  # Tests performed
    diagnosis = db.Column(db.Text, nullable=False)
    prescription = db.Column(db.Text)
    medicines = db.Column(db.Text)  # Structured medicines list (e.g., "Medicine 1 1-0-1, Medicine 2 0-1-1")
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Treatment {self.id} - Appointment {self.appointment_id}>'

class DoctorAvailability(db.Model):
    """Doctor Availability model for structured 7-day availability"""
    __tablename__ = 'doctor_availability'
    
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)  # Date for the availability slot
    morning_start = db.Column(db.Time)  # Morning slot start time (e.g., 08:00)
    morning_end = db.Column(db.Time)  # Morning slot end time (e.g., 12:00)
    evening_start = db.Column(db.Time)  # Evening slot start time (e.g., 16:00)
    evening_end = db.Column(db.Time)  # Evening slot end time (e.g., 21:00)
    is_available = db.Column(db.Boolean, default=True)  # Whether doctor is available on this date
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Unique constraint: one availability record per doctor per date
    __table_args__ = (db.UniqueConstraint('doctor_id', 'date', name='unique_doctor_date'),)
    
    def __repr__(self):
        return f'<DoctorAvailability {self.id} - Doctor {self.doctor_id} - {self.date}>'

