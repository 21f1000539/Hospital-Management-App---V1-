from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash, generate_password_hash
from database import db
from models import Admin, Doctor, Patient, Department, Appointment, Treatment
from functools import wraps
from datetime import datetime, date, timedelta
from sqlalchemy import or_, and_

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital_management.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize db with app
db.init_app(app)

# Role-based decorator for route protection
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def doctor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'doctor':
            flash('Doctor access required.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def patient_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'patient':
            flash('Patient access required.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    """Home page - redirects to login if not authenticated"""
    if 'user_id' in session:
        role = session.get('role')
        if role == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif role == 'doctor':
            return redirect(url_for('doctor_dashboard'))
        elif role == 'patient':
            return redirect(url_for('patient_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page for all user types"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        
        if not username or not password or not role:
            flash('Please fill in all fields.', 'danger')
            return render_template('login.html')
        
        user = None
        if role == 'admin':
            user = Admin.query.filter_by(username=username).first()
        elif role == 'doctor':
            user = Doctor.query.filter_by(username=username, is_active=True).first()
        elif role == 'patient':
            user = Patient.query.filter_by(username=username, is_active=True).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = role
            session['name'] = user.name
            
            flash(f'Welcome back, {user.name}!', 'success')
            if role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif role == 'doctor':
                return redirect(url_for('doctor_dashboard'))
            elif role == 'patient':
                return redirect(url_for('patient_dashboard'))
        else:
            flash('Invalid username, password, or account is inactive.', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Patient registration page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        email = request.form.get('email')
        name = request.form.get('name')
        phone = request.form.get('phone')
        address = request.form.get('address')
        date_of_birth = request.form.get('date_of_birth')
        gender = request.form.get('gender')
        
        # Validation
        if not username or not password or not email or not name:
            flash('Please fill in all required fields.', 'danger')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')
        
        # Check if username already exists
        if Patient.query.filter_by(username=username).first():
            flash('Username already exists. Please choose another.', 'danger')
            return render_template('register.html')
        
        # Check if email already exists
        if Patient.query.filter_by(email=email).first():
            flash('Email already exists. Please use another email.', 'danger')
            return render_template('register.html')
        
        # Parse date of birth
        dob = None
        if date_of_birth:
            try:
                dob = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid date format.', 'danger')
                return render_template('register.html')
        
        # Create new patient
        try:
            new_patient = Patient(
                username=username,
                password=generate_password_hash(password),
                email=email,
                name=name,
                phone=phone,
                address=address,
                date_of_birth=dob,
                gender=gender,
                is_active=True
            )
            db.session.add(new_patient)
            db.session.commit()
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'danger')
            return render_template('register.html')
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    """Logout and clear session"""
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))

# Admin Dashboard
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Admin dashboard"""
    # Get statistics
    total_doctors = Doctor.query.count()
    total_patients = Patient.query.count()
    total_appointments = Appointment.query.count()
    upcoming_appointments = Appointment.query.filter(
        Appointment.date >= date.today(),
        Appointment.status == 'Booked'
    ).count()
    
    return render_template('admin/dashboard.html',
                         total_doctors=total_doctors,
                         total_patients=total_patients,
                         total_appointments=total_appointments,
                         upcoming_appointments=upcoming_appointments)

# Doctor Dashboard
@app.route('/doctor/dashboard')
@doctor_required
def doctor_dashboard():
    """Doctor dashboard"""
    doctor_id = session.get('user_id')
    doctor = Doctor.query.get(doctor_id)
    
    if not doctor:
        flash('Doctor not found.', 'danger')
        return redirect(url_for('login'))
    
    # Get today's appointments
    today = date.today()
    today_appointments = Appointment.query.filter(
        Appointment.doctor_id == doctor_id,
        Appointment.date == today,
        Appointment.status == 'Booked'
    ).order_by(Appointment.time).all()
    
    # Get upcoming appointments (next 7 days)
    week_end = today + timedelta(days=7)
    upcoming_appointments = Appointment.query.filter(
        Appointment.doctor_id == doctor_id,
        Appointment.date >= today,
        Appointment.date <= week_end,
        Appointment.status == 'Booked'
    ).order_by(Appointment.date, Appointment.time).all()
    
    # Get all assigned patients
    patient_ids = db.session.query(Appointment.patient_id).filter(
        Appointment.doctor_id == doctor_id
    ).distinct().all()
    assigned_patients = Patient.query.filter(
        Patient.id.in_([pid[0] for pid in patient_ids])
    ).all()
    
    return render_template('doctor/dashboard.html',
                         doctor=doctor,
                         today_appointments=today_appointments,
                         upcoming_appointments=upcoming_appointments,
                         assigned_patients=assigned_patients)

# Patient Dashboard
@app.route('/patient/dashboard')
@patient_required
def patient_dashboard():
    """Patient dashboard"""
    patient_id = session.get('user_id')
    patient = Patient.query.get(patient_id)
    
    if not patient:
        flash('Patient not found.', 'danger')
        return redirect(url_for('login'))
    
    # Get all departments
    departments = Department.query.all()
    
    # Get all doctors with their availability
    doctors = Doctor.query.filter_by(is_active=True).all()
    
    # Get upcoming appointments
    today = date.today()
    upcoming_appointments = Appointment.query.filter(
        Appointment.patient_id == patient_id,
        Appointment.date >= today,
        Appointment.status == 'Booked'
    ).order_by(Appointment.date, Appointment.time).all()
    
    # Get past appointments (date < today) and completed appointments
    past_appointments = Appointment.query.filter(
        or_(
            and_(Appointment.patient_id == patient_id, Appointment.date < today),
            and_(Appointment.patient_id == patient_id, Appointment.status == 'Completed')
        )
    ).order_by(Appointment.date.desc(), Appointment.time.desc()).all()
    
    # Remove duplicates and filter out upcoming booked appointments
    past_appointments = [apt for apt in past_appointments if apt.status != 'Booked' or apt.date < today]
    
    return render_template('patient/dashboard.html',
                         patient=patient,
                         departments=departments,
                         doctors=doctors,
                         upcoming_appointments=upcoming_appointments,
                         past_appointments=past_appointments)

if __name__ == '__main__':
    app.run(debug=True)
