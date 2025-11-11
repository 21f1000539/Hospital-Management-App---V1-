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
    active_doctors = Doctor.query.filter_by(is_active=True).count()
    total_patients = Patient.query.count()
    active_patients = Patient.query.filter_by(is_active=True).count()
    total_appointments = Appointment.query.count()
    upcoming_appointments = Appointment.query.filter(
        Appointment.date >= date.today(),
        Appointment.status == 'Booked'
    ).count()
    
    # Get recent appointments
    recent_appointments = Appointment.query.order_by(
        Appointment.date.desc(), Appointment.time.desc()
    ).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_doctors=total_doctors,
                         active_doctors=active_doctors,
                         total_patients=total_patients,
                         active_patients=active_patients,
                         total_appointments=total_appointments,
                         upcoming_appointments=upcoming_appointments,
                         recent_appointments=recent_appointments)

# Admin - Doctor Management
@app.route('/admin/doctors')
@admin_required
def admin_doctors():
    """View all doctors"""
    doctors = Doctor.query.order_by(Doctor.name).all()
    departments = Department.query.all()
    return render_template('admin/doctors.html', doctors=doctors, departments=departments)

@app.route('/admin/doctors/add', methods=['GET', 'POST'])
@admin_required
def admin_add_doctor():
    """Add a new doctor"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        name = request.form.get('name')
        phone = request.form.get('phone')
        specialization = request.form.get('specialization')
        department_id = request.form.get('department_id') or None
        availability = request.form.get('availability')
        
        if not username or not password or not email or not name or not specialization:
            flash('Please fill in all required fields.', 'danger')
            departments = Department.query.all()
            return render_template('admin/add_doctor.html', departments=departments)
        
        # Check if username already exists
        if Doctor.query.filter_by(username=username).first():
            flash('Username already exists. Please choose another.', 'danger')
            departments = Department.query.all()
            return render_template('admin/add_doctor.html', departments=departments)
        
        # Check if email already exists
        if Doctor.query.filter_by(email=email).first():
            flash('Email already exists. Please use another email.', 'danger')
            departments = Department.query.all()
            return render_template('admin/add_doctor.html', departments=departments)
        
        try:
            new_doctor = Doctor(
                username=username,
                password=generate_password_hash(password),
                email=email,
                name=name,
                phone=phone,
                specialization=specialization,
                department_id=int(department_id) if department_id else None,
                availability=availability,
                is_active=True
            )
            db.session.add(new_doctor)
            db.session.commit()
            
            flash(f'Doctor {name} added successfully!', 'success')
            return redirect(url_for('admin_doctors'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while adding the doctor. Please try again.', 'danger')
            departments = Department.query.all()
            return render_template('admin/add_doctor.html', departments=departments)
    
    departments = Department.query.all()
    return render_template('admin/add_doctor.html', departments=departments)

@app.route('/admin/doctors/<int:doctor_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_edit_doctor(doctor_id):
    """Edit a doctor"""
    doctor = Doctor.query.get_or_404(doctor_id)
    
    if request.method == 'POST':
        doctor.email = request.form.get('email')
        doctor.name = request.form.get('name')
        doctor.phone = request.form.get('phone')
        doctor.specialization = request.form.get('specialization')
        department_id = request.form.get('department_id') or None
        doctor.department_id = int(department_id) if department_id else None
        doctor.availability = request.form.get('availability')
        
        # Update password if provided
        new_password = request.form.get('password')
        if new_password:
            doctor.password = generate_password_hash(new_password)
        
        try:
            db.session.commit()
            flash(f'Doctor {doctor.name} updated successfully!', 'success')
            return redirect(url_for('admin_doctors'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating the doctor. Please try again.', 'danger')
    
    departments = Department.query.all()
    return render_template('admin/edit_doctor.html', doctor=doctor, departments=departments)

@app.route('/admin/doctors/<int:doctor_id>/delete', methods=['POST'])
@admin_required
def admin_delete_doctor(doctor_id):
    """Delete or blacklist a doctor"""
    doctor = Doctor.query.get_or_404(doctor_id)
    action = request.form.get('action')
    
    try:
        if action == 'blacklist':
            doctor.is_active = False
            flash(f'Doctor {doctor.name} has been blacklisted.', 'warning')
        elif action == 'activate':
            doctor.is_active = True
            flash(f'Doctor {doctor.name} has been activated.', 'success')
        elif action == 'delete':
            # Check if doctor has appointments
            appointments = Appointment.query.filter_by(doctor_id=doctor_id).count()
            if appointments > 0:
                flash('Cannot delete doctor with existing appointments. Blacklist instead.', 'danger')
                return redirect(url_for('admin_doctors'))
            db.session.delete(doctor)
            flash(f'Doctor {doctor.name} has been deleted.', 'success')
        
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash('An error occurred. Please try again.', 'danger')
    
    return redirect(url_for('admin_doctors'))

# Admin - Patient Management
@app.route('/admin/patients')
@admin_required
def admin_patients():
    """View all patients"""
    search_query = request.args.get('search', '')
    patients = Patient.query
    
    if search_query:
        search_filters = [
            Patient.name.contains(search_query),
            Patient.username.contains(search_query),
            Patient.email.contains(search_query),
            Patient.phone.contains(search_query)
        ]
        # Add ID filter if search query is a number
        if search_query.isdigit():
            search_filters.append(Patient.id == int(search_query))
        
        patients = patients.filter(or_(*search_filters))
    
    patients = patients.order_by(Patient.name).all()
    return render_template('admin/patients.html', patients=patients, search_query=search_query)

@app.route('/admin/patients/<int:patient_id>')
@admin_required
def admin_view_patient(patient_id):
    """View patient details"""
    patient = Patient.query.get_or_404(patient_id)
    appointments = Appointment.query.filter_by(patient_id=patient_id).order_by(
        Appointment.date.desc(), Appointment.time.desc()
    ).all()
    
    # Get treatments for these appointments
    appointment_ids = [apt.id for apt in appointments]
    treatments = {}
    if appointment_ids:
        treatment_list = Treatment.query.filter(
            Treatment.appointment_id.in_(appointment_ids)
        ).all()
        treatments = {t.appointment_id: t for t in treatment_list}
    
    return render_template('admin/view_patient.html', 
                         patient=patient, 
                         appointments=appointments,
                         treatments=treatments)

@app.route('/admin/patients/<int:patient_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_edit_patient(patient_id):
    """Edit a patient"""
    patient = Patient.query.get_or_404(patient_id)
    
    if request.method == 'POST':
        patient.email = request.form.get('email')
        patient.name = request.form.get('name')
        patient.phone = request.form.get('phone')
        patient.address = request.form.get('address')
        patient.gender = request.form.get('gender')
        
        date_of_birth = request.form.get('date_of_birth')
        if date_of_birth:
            try:
                patient.date_of_birth = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid date format.', 'danger')
                return render_template('admin/edit_patient.html', patient=patient)
        
        # Update password if provided
        new_password = request.form.get('password')
        if new_password:
            patient.password = generate_password_hash(new_password)
        
        try:
            db.session.commit()
            flash(f'Patient {patient.name} updated successfully!', 'success')
            return redirect(url_for('admin_view_patient', patient_id=patient_id))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating the patient. Please try again.', 'danger')
    
    return render_template('admin/edit_patient.html', patient=patient)

@app.route('/admin/patients/<int:patient_id>/delete', methods=['POST'])
@admin_required
def admin_delete_patient(patient_id):
    """Delete or blacklist a patient"""
    patient = Patient.query.get_or_404(patient_id)
    action = request.form.get('action')
    
    try:
        if action == 'blacklist':
            patient.is_active = False
            flash(f'Patient {patient.name} has been blacklisted.', 'warning')
        elif action == 'activate':
            patient.is_active = True
            flash(f'Patient {patient.name} has been activated.', 'success')
        elif action == 'delete':
            # Check if patient has appointments
            appointments = Appointment.query.filter_by(patient_id=patient_id).count()
            if appointments > 0:
                flash('Cannot delete patient with existing appointments. Blacklist instead.', 'danger')
                return redirect(url_for('admin_patients'))
            db.session.delete(patient)
            flash(f'Patient {patient.name} has been deleted.', 'success')
        
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash('An error occurred. Please try again.', 'danger')
    
    return redirect(url_for('admin_patients'))

# Admin - Appointment Management
@app.route('/admin/appointments')
@admin_required
def admin_appointments():
    """View all appointments"""
    status_filter = request.args.get('status', '')
    date_filter = request.args.get('date', '')
    doctor_filter = request.args.get('doctor', '')
    patient_filter = request.args.get('patient', '')
    
    appointments = Appointment.query
    
    if status_filter:
        appointments = appointments.filter(Appointment.status == status_filter)
    
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            appointments = appointments.filter(Appointment.date == filter_date)
        except ValueError:
            pass
    
    if doctor_filter:
        appointments = appointments.filter(Appointment.doctor_id == int(doctor_filter))
    
    if patient_filter:
        appointments = appointments.filter(Appointment.patient_id == int(patient_filter))
    
    appointments = appointments.order_by(Appointment.date.desc(), Appointment.time.desc()).all()
    
    # Get all doctors and patients for filter dropdowns
    doctors = Doctor.query.filter_by(is_active=True).order_by(Doctor.name).all()
    patients = Patient.query.filter_by(is_active=True).order_by(Patient.name).all()
    
    return render_template('admin/appointments.html', 
                         appointments=appointments,
                         status_filter=status_filter,
                         date_filter=date_filter,
                         doctor_filter=doctor_filter,
                         patient_filter=patient_filter,
                         doctors=doctors,
                         patients=patients)

# Admin - Search
@app.route('/admin/search')
@admin_required
def admin_search():
    """Search for patients and doctors"""
    query = request.args.get('q', '')
    search_type = request.args.get('type', 'all')
    
    results = {
        'patients': [],
        'doctors': []
    }
    
    if query:
        if search_type in ['all', 'patients']:
            patient_filters = [
                Patient.name.contains(query),
                Patient.username.contains(query),
                Patient.email.contains(query),
                Patient.phone.contains(query)
            ]
            if query.isdigit():
                patient_filters.append(Patient.id == int(query))
            results['patients'] = Patient.query.filter(or_(*patient_filters)).all()
        
        if search_type in ['all', 'doctors']:
            doctor_filters = [
                Doctor.name.contains(query),
                Doctor.username.contains(query),
                Doctor.specialization.contains(query),
                Doctor.email.contains(query)
            ]
            if query.isdigit():
                doctor_filters.append(Doctor.id == int(query))
            results['doctors'] = Doctor.query.filter(or_(*doctor_filters)).all()
    
    return render_template('admin/search.html', results=results, query=query, search_type=search_type)

# Admin - Department Management
@app.route('/admin/departments')
@admin_required
def admin_departments():
    """View all departments"""
    departments = Department.query.order_by(Department.name).all()
    return render_template('admin/departments.html', departments=departments)

@app.route('/admin/departments/add', methods=['GET', 'POST'])
@admin_required
def admin_add_department():
    """Add a new department"""
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        if not name:
            flash('Department name is required.', 'danger')
            return render_template('admin/add_department.html')
        
        # Check if department already exists
        if Department.query.filter_by(name=name).first():
            flash('Department already exists.', 'danger')
            return render_template('admin/add_department.html')
        
        try:
            new_department = Department(name=name, description=description)
            db.session.add(new_department)
            db.session.commit()
            
            flash(f'Department {name} added successfully!', 'success')
            return redirect(url_for('admin_departments'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while adding the department. Please try again.', 'danger')
    
    return render_template('admin/add_department.html')

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
        Appointment.status.in_(['Booked', 'Completed'])
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
    assigned_patients = []
    if patient_ids:
        assigned_patients = Patient.query.filter(
            Patient.id.in_([pid[0] for pid in patient_ids])
        ).all()
    
    # Get statistics
    total_appointments_today = len(today_appointments)
    completed_today = len([apt for apt in today_appointments if apt.status == 'Completed'])
    upcoming_count = len(upcoming_appointments)
    
    return render_template('doctor/dashboard.html',
                         doctor=doctor,
                         today_appointments=today_appointments,
                         upcoming_appointments=upcoming_appointments,
                         assigned_patients=assigned_patients,
                         total_appointments_today=total_appointments_today,
                         completed_today=completed_today,
                         upcoming_count=upcoming_count)

# Doctor - View All Appointments
@app.route('/doctor/appointments')
@doctor_required
def doctor_appointments():
    """View all appointments for doctor"""
    doctor_id = session.get('user_id')
    status_filter = request.args.get('status', '')
    date_filter = request.args.get('date', '')
    
    appointments = Appointment.query.filter(Appointment.doctor_id == doctor_id)
    
    if status_filter:
        appointments = appointments.filter(Appointment.status == status_filter)
    
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            appointments = appointments.filter(Appointment.date == filter_date)
        except ValueError:
            pass
    
    appointments = appointments.order_by(Appointment.date.desc(), Appointment.time.desc()).all()
    
    return render_template('doctor/appointments.html',
                         appointments=appointments,
                         status_filter=status_filter,
                         date_filter=date_filter)

# Doctor - View Appointment Details
@app.route('/doctor/appointments/<int:appointment_id>')
@doctor_required
def doctor_view_appointment(appointment_id):
    """View appointment details"""
    doctor_id = session.get('user_id')
    appointment = Appointment.query.get_or_404(appointment_id)
    
    # Verify appointment belongs to this doctor
    if appointment.doctor_id != doctor_id:
        flash('You do not have permission to view this appointment.', 'danger')
        return redirect(url_for('doctor_dashboard'))
    
    # Get patient's previous appointments with this doctor for context
    previous_appointments = Appointment.query.filter(
        Appointment.patient_id == appointment.patient_id,
        Appointment.doctor_id == doctor_id,
        Appointment.id != appointment_id,
        Appointment.status == 'Completed'
    ).order_by(Appointment.date.desc()).limit(5).all()
    
    return render_template('doctor/view_appointment.html', 
                         appointment=appointment,
                         previous_appointments=previous_appointments)

# Doctor - Update Appointment Status
@app.route('/doctor/appointments/<int:appointment_id>/update-status', methods=['POST'])
@doctor_required
def doctor_update_appointment_status(appointment_id):
    """Update appointment status (Completed or Cancelled)"""
    doctor_id = session.get('user_id')
    appointment = Appointment.query.get_or_404(appointment_id)
    
    # Verify appointment belongs to this doctor
    if appointment.doctor_id != doctor_id:
        flash('You do not have permission to update this appointment.', 'danger')
        return redirect(url_for('doctor_dashboard'))
    
    new_status = request.form.get('status')
    
    if new_status not in ['Completed', 'Cancelled']:
        flash('Invalid status.', 'danger')
        return redirect(url_for('doctor_view_appointment', appointment_id=appointment_id))
    
    try:
        appointment.status = new_status
        appointment.updated_at = datetime.utcnow()
        db.session.commit()
        
        flash(f'Appointment status updated to {new_status}.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while updating the appointment.', 'danger')
    
    return redirect(url_for('doctor_view_appointment', appointment_id=appointment_id))

# Doctor - Add Treatment
@app.route('/doctor/appointments/<int:appointment_id>/treatment', methods=['GET', 'POST'])
@doctor_required
def doctor_add_treatment(appointment_id):
    """Add treatment for an appointment"""
    doctor_id = session.get('user_id')
    appointment = Appointment.query.get_or_404(appointment_id)
    
    # Verify appointment belongs to this doctor
    if appointment.doctor_id != doctor_id:
        flash('You do not have permission to add treatment for this appointment.', 'danger')
        return redirect(url_for('doctor_dashboard'))
    
    if request.method == 'POST':
        diagnosis = request.form.get('diagnosis')
        prescription = request.form.get('prescription')
        notes = request.form.get('notes')
        
        if not diagnosis:
            flash('Diagnosis is required.', 'danger')
            return render_template('doctor/add_treatment.html', appointment=appointment)
        
        try:
            # Check if treatment already exists
            treatment = Treatment.query.filter_by(appointment_id=appointment_id).first()
            
            if treatment:
                # Update existing treatment
                treatment.diagnosis = diagnosis
                treatment.prescription = prescription
                treatment.notes = notes
                treatment.updated_at = datetime.utcnow()
            else:
                # Create new treatment
                treatment = Treatment(
                    appointment_id=appointment_id,
                    diagnosis=diagnosis,
                    prescription=prescription,
                    notes=notes
                )
                db.session.add(treatment)
                # Mark appointment as completed
                appointment.status = 'Completed'
                appointment.updated_at = datetime.utcnow()
            
            db.session.commit()
            flash('Treatment recorded successfully!', 'success')
            return redirect(url_for('doctor_view_appointment', appointment_id=appointment_id))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while recording treatment.', 'danger')
    
    # Check if treatment already exists
    treatment = Treatment.query.filter_by(appointment_id=appointment_id).first()
    return render_template('doctor/add_treatment.html', appointment=appointment, treatment=treatment)

# Doctor - View Patient History
@app.route('/doctor/patients/<int:patient_id>/history')
@doctor_required
def doctor_view_patient_history(patient_id):
    """View complete patient medical history"""
    doctor_id = session.get('user_id')
    patient = Patient.query.get_or_404(patient_id)
    
    # Get all appointments for this patient with this doctor
    appointments = Appointment.query.filter(
        Appointment.patient_id == patient_id,
        Appointment.doctor_id == doctor_id
    ).order_by(Appointment.date.desc(), Appointment.time.desc()).all()
    
    # Get treatments for these appointments
    treatment_dict = {}
    if appointments:
        appointment_ids = [apt.id for apt in appointments]
        treatments = Treatment.query.filter(
            Treatment.appointment_id.in_(appointment_ids)
        ).all()
        # Create a dictionary for easy lookup
        treatment_dict = {t.appointment_id: t for t in treatments}
    
    return render_template('doctor/patient_history.html',
                         patient=patient,
                         appointments=appointments,
                         treatment_dict=treatment_dict)

# Doctor - Update Availability
@app.route('/doctor/availability', methods=['GET', 'POST'])
@doctor_required
def doctor_update_availability():
    """Update doctor availability for next 7 days"""
    doctor_id = session.get('user_id')
    doctor = Doctor.query.get(doctor_id)
    
    if not doctor:
        flash('Doctor not found.', 'danger')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        availability = request.form.get('availability')
        
        try:
            doctor.availability = availability
            db.session.commit()
            flash('Availability updated successfully!', 'success')
            return redirect(url_for('doctor_dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating availability.', 'danger')
    
    return render_template('doctor/availability.html', doctor=doctor)

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
    
    # Get all active doctors
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
    
    # Get statistics
    upcoming_count = len(upcoming_appointments)
    past_count = len(past_appointments)
    
    return render_template('patient/dashboard.html',
                         patient=patient,
                         departments=departments,
                         doctors=doctors,
                         upcoming_appointments=upcoming_appointments,
                         past_appointments=past_appointments,
                         upcoming_count=upcoming_count,
                         past_count=past_count)

# Patient - Profile Management
@app.route('/patient/profile', methods=['GET', 'POST'])
@patient_required
def patient_profile():
    """View and update patient profile"""
    patient_id = session.get('user_id')
    patient = Patient.query.get(patient_id)
    
    if not patient:
        flash('Patient not found.', 'danger')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        patient.email = request.form.get('email')
        patient.name = request.form.get('name')
        patient.phone = request.form.get('phone')
        patient.address = request.form.get('address')
        patient.gender = request.form.get('gender')
        
        date_of_birth = request.form.get('date_of_birth')
        if date_of_birth:
            try:
                patient.date_of_birth = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid date format.', 'danger')
                return render_template('patient/profile.html', patient=patient)
        
        # Update password if provided
        new_password = request.form.get('password')
        if new_password:
            patient.password = generate_password_hash(new_password)
        
        try:
            db.session.commit()
            session['name'] = patient.name  # Update session name
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('patient_dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating your profile.', 'danger')
    
    return render_template('patient/profile.html', patient=patient)

# Patient - Search Doctors
@app.route('/patient/doctors')
@patient_required
def patient_search_doctors():
    """Search and view doctors"""
    search_query = request.args.get('search', '')
    specialization_filter = request.args.get('specialization', '')
    department_filter = request.args.get('department', '')
    
    doctors = Doctor.query.filter_by(is_active=True)
    
    if search_query:
        doctors = doctors.filter(
            or_(
                Doctor.name.contains(search_query),
                Doctor.specialization.contains(search_query),
                Doctor.email.contains(search_query)
            )
        )
    
    if specialization_filter:
        doctors = doctors.filter(Doctor.specialization.contains(specialization_filter))
    
    if department_filter:
        doctors = doctors.filter(Doctor.department_id == int(department_filter))
    
    doctors = doctors.order_by(Doctor.name).all()
    departments = Department.query.all()
    
    # Get unique specializations
    specializations = db.session.query(Doctor.specialization).filter_by(is_active=True).distinct().all()
    specializations = [spec[0] for spec in specializations]
    
    return render_template('patient/doctors.html',
                         doctors=doctors,
                         departments=departments,
                         specializations=specializations,
                         search_query=search_query,
                         specialization_filter=specialization_filter,
                         department_filter=department_filter)

# Patient - View Doctor
@app.route('/patient/doctors/<int:doctor_id>')
@patient_required
def patient_view_doctor(doctor_id):
    """View doctor details"""
    doctor = Doctor.query.filter_by(id=doctor_id, is_active=True).first_or_404()
    return render_template('patient/view_doctor.html', doctor=doctor)

# Helper function to check appointment availability
def check_appointment_availability(doctor_id, apt_date, apt_time, exclude_appointment_id=None):
    """Check if a time slot is available for booking"""
    query = Appointment.query.filter(
        Appointment.doctor_id == doctor_id,
        Appointment.date == apt_date,
        Appointment.time == apt_time,
        Appointment.status.in_(['Booked', 'Completed'])  # Only Booked and Completed block the slot
    )
    
    if exclude_appointment_id:
        query = query.filter(Appointment.id != exclude_appointment_id)
    
    existing_appointment = query.first()
    return existing_appointment is None

# Patient - Book Appointment
@app.route('/patient/appointments/book/<int:doctor_id>', methods=['GET', 'POST'])
@patient_required
def patient_book_appointment(doctor_id):
    """Book an appointment with a doctor"""
    patient_id = session.get('user_id')
    doctor = Doctor.query.filter_by(id=doctor_id, is_active=True).first_or_404()
    
    if request.method == 'POST':
        appointment_date = request.form.get('date')
        appointment_time = request.form.get('time')
        reason = request.form.get('reason')
        
        if not appointment_date or not appointment_time:
            flash('Please select both date and time.', 'danger')
            # Get booked appointments for the selected date to show conflicts
            selected_date = request.form.get('date')
            if selected_date:
                try:
                    check_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
                    booked_appointments = Appointment.query.filter(
                        Appointment.doctor_id == doctor_id,
                        Appointment.date == check_date,
                        Appointment.status.in_(['Booked', 'Completed'])
                    ).order_by(Appointment.time).all()
                    return render_template('patient/book_appointment.html', 
                                         doctor=doctor, 
                                         selected_date=selected_date,
                                         booked_appointments=booked_appointments)
                except ValueError:
                    pass
            return render_template('patient/book_appointment.html', doctor=doctor)
        
        try:
            apt_date = datetime.strptime(appointment_date, '%Y-%m-%d').date()
            apt_time = datetime.strptime(appointment_time, '%H:%M').time()
        except ValueError:
            flash('Invalid date or time format.', 'danger')
            return render_template('patient/book_appointment.html', doctor=doctor)
        
        # Check if date is in the past
        if apt_date < date.today():
            flash('Cannot book appointments in the past.', 'danger')
            return render_template('patient/book_appointment.html', doctor=doctor)
        
        # Check if date is more than 7 days in the future
        if apt_date > date.today() + timedelta(days=7):
            flash('Can only book appointments up to 7 days in advance.', 'danger')
            return render_template('patient/book_appointment.html', doctor=doctor)
        
        # Check for double booking (same doctor, same date, same time, status Booked or Completed)
        if not check_appointment_availability(doctor_id, apt_date, apt_time):
            # Get the conflicting appointment details
            conflicting = Appointment.query.filter(
                Appointment.doctor_id == doctor_id,
                Appointment.date == apt_date,
                Appointment.time == apt_time,
                Appointment.status.in_(['Booked', 'Completed'])
            ).first()
            
            if conflicting:
                flash(f'This time slot is already booked by another patient. Please choose another time.', 'danger')
            else:
                flash('This time slot is not available. Please choose another time.', 'danger')
            
            # Show booked appointments for the selected date
            booked_appointments = Appointment.query.filter(
                Appointment.doctor_id == doctor_id,
                Appointment.date == apt_date,
                Appointment.status.in_(['Booked', 'Completed'])
            ).order_by(Appointment.time).all()
            
            return render_template('patient/book_appointment.html', 
                                 doctor=doctor,
                                 selected_date=appointment_date,
                                 selected_time=appointment_time,
                                 booked_appointments=booked_appointments)
        
        # Create new appointment
        try:
            new_appointment = Appointment(
                patient_id=patient_id,
                doctor_id=doctor_id,
                date=apt_date,
                time=apt_time,
                status='Booked',
                reason=reason
            )
            db.session.add(new_appointment)
            db.session.commit()
            
            flash(f'Appointment booked successfully for {apt_date.strftime("%B %d, %Y")} at {apt_time.strftime("%I:%M %p")}!', 'success')
            return redirect(url_for('patient_dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while booking the appointment. Please try again.', 'danger')
    
    # For GET request, check if a date is selected to show booked slots
    selected_date = request.args.get('date', '')
    booked_appointments = []
    if selected_date:
        try:
            check_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
            booked_appointments = Appointment.query.filter(
                Appointment.doctor_id == doctor_id,
                Appointment.date == check_date,
                Appointment.status.in_(['Booked', 'Completed'])
            ).order_by(Appointment.time).all()
        except ValueError:
            pass
    
    return render_template('patient/book_appointment.html', 
                         doctor=doctor,
                         selected_date=selected_date,
                         booked_appointments=booked_appointments)

# Patient - View Appointment
@app.route('/patient/appointments/<int:appointment_id>')
@patient_required
def patient_view_appointment(appointment_id):
    """View appointment details"""
    patient_id = session.get('user_id')
    appointment = Appointment.query.get_or_404(appointment_id)
    
    # Verify appointment belongs to this patient
    if appointment.patient_id != patient_id:
        flash('You do not have permission to view this appointment.', 'danger')
        return redirect(url_for('patient_dashboard'))
    
    return render_template('patient/view_appointment.html', appointment=appointment)

# Patient - Cancel Appointment
@app.route('/patient/appointments/<int:appointment_id>/cancel', methods=['POST'])
@patient_required
def patient_cancel_appointment(appointment_id):
    """Cancel an appointment"""
    patient_id = session.get('user_id')
    appointment = Appointment.query.get_or_404(appointment_id)
    
    # Verify appointment belongs to this patient
    if appointment.patient_id != patient_id:
        flash('You do not have permission to cancel this appointment.', 'danger')
        return redirect(url_for('patient_dashboard'))
    
    # Check if appointment can be cancelled
    if appointment.status != 'Booked':
        flash('Only booked appointments can be cancelled.', 'danger')
        return redirect(url_for('patient_view_appointment', appointment_id=appointment_id))
    
    try:
        appointment.status = 'Cancelled'
        appointment.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Appointment cancelled successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while cancelling the appointment.', 'danger')
    
    return redirect(url_for('patient_dashboard'))

# Patient - Reschedule Appointment
@app.route('/patient/appointments/<int:appointment_id>/reschedule', methods=['GET', 'POST'])
@patient_required
def patient_reschedule_appointment(appointment_id):
    """Reschedule an appointment"""
    patient_id = session.get('user_id')
    appointment = Appointment.query.get_or_404(appointment_id)
    
    # Verify appointment belongs to this patient
    if appointment.patient_id != patient_id:
        flash('You do not have permission to reschedule this appointment.', 'danger')
        return redirect(url_for('patient_dashboard'))
    
    # Check if appointment can be rescheduled
    if appointment.status != 'Booked':
        flash('Only booked appointments can be rescheduled.', 'danger')
        return redirect(url_for('patient_view_appointment', appointment_id=appointment_id))
    
    if request.method == 'POST':
        new_date = request.form.get('date')
        new_time = request.form.get('time')
        
        if not new_date or not new_time:
            flash('Please select both date and time.', 'danger')
            return render_template('patient/reschedule_appointment.html', appointment=appointment)
        
        try:
            apt_date = datetime.strptime(new_date, '%Y-%m-%d').date()
            apt_time = datetime.strptime(new_time, '%H:%M').time()
        except ValueError:
            flash('Invalid date or time format.', 'danger')
            return render_template('patient/reschedule_appointment.html', appointment=appointment)
        
        # Check if date is in the past
        if apt_date < date.today():
            flash('Cannot reschedule to a past date.', 'danger')
            return render_template('patient/reschedule_appointment.html', appointment=appointment)
        
        # Check if date is more than 7 days in the future
        if apt_date > date.today() + timedelta(days=7):
            flash('Can only reschedule appointments up to 7 days in advance.', 'danger')
            return render_template('patient/reschedule_appointment.html', appointment=appointment)
        
        # Check for double booking (same doctor, same date, same time, status Booked or Completed, excluding current appointment)
        if not check_appointment_availability(appointment.doctor_id, apt_date, apt_time, exclude_appointment_id=appointment_id):
            conflicting = Appointment.query.filter(
                Appointment.doctor_id == appointment.doctor_id,
                Appointment.date == apt_date,
                Appointment.time == apt_time,
                Appointment.status.in_(['Booked', 'Completed']),
                Appointment.id != appointment_id
            ).first()
            
            if conflicting:
                flash(f'This time slot is already booked by another patient. Please choose another time.', 'danger')
            else:
                flash('This time slot is not available. Please choose another time.', 'danger')
            
            # Show booked appointments for the selected date
            booked_appointments = Appointment.query.filter(
                Appointment.doctor_id == appointment.doctor_id,
                Appointment.date == apt_date,
                Appointment.status.in_(['Booked', 'Completed']),
                Appointment.id != appointment_id
            ).order_by(Appointment.time).all()
            
            return render_template('patient/reschedule_appointment.html', 
                                 appointment=appointment,
                                 selected_date=new_date,
                                 selected_time=new_time,
                                 booked_appointments=booked_appointments)
        
        # Update appointment
        try:
            appointment.date = apt_date
            appointment.time = apt_time
            appointment.updated_at = datetime.utcnow()
            db.session.commit()
            
            flash('Appointment rescheduled successfully!', 'success')
            return redirect(url_for('patient_dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while rescheduling the appointment.', 'danger')
    
    # For GET request, check if a date is selected to show booked slots
    selected_date = request.args.get('date', '')
    booked_appointments = []
    if selected_date:
        try:
            check_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
            booked_appointments = Appointment.query.filter(
                Appointment.doctor_id == appointment.doctor_id,
                Appointment.date == check_date,
                Appointment.status.in_(['Booked', 'Completed']),
                Appointment.id != appointment_id
            ).order_by(Appointment.time).all()
        except ValueError:
            pass
    
    return render_template('patient/reschedule_appointment.html', 
                         appointment=appointment,
                         selected_date=selected_date,
                         booked_appointments=booked_appointments)

if __name__ == '__main__':
    app.run(debug=True)
