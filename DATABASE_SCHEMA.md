# Database Schema Documentation

## Overview
This document describes the database schema for the Hospital Management System.

## Tables

### 1. Admin
Stores hospital administrator accounts (predefined, no registration allowed).

**Fields:**
- `id` (Integer, Primary Key)
- `username` (String, Unique, Not Null)
- `password` (String, Not Null) - Hashed password
- `email` (String, Unique, Not Null)
- `name` (String, Not Null)
- `created_at` (DateTime)

### 2. Department
Stores medical departments/specializations.

**Fields:**
- `id` (Integer, Primary Key)
- `name` (String, Unique, Not Null)
- `description` (Text)
- `created_at` (DateTime)

**Relationships:**
- One-to-Many with Doctor

### 3. Doctor
Stores doctor accounts and information.

**Fields:**
- `id` (Integer, Primary Key)
- `username` (String, Unique, Not Null)
- `password` (String, Not Null) - Hashed password
- `email` (String, Unique, Not Null)
- `name` (String, Not Null)
- `phone` (String)
- `specialization` (String, Not Null)
- `department_id` (Integer, Foreign Key → Department.id, Nullable)
- `availability` (String) - JSON string for availability schedule (next 7 days)
- `is_active` (Boolean, Default: True)
- `created_at` (DateTime)

**Relationships:**
- Many-to-One with Department
- One-to-Many with Appointment

### 4. Patient
Stores patient accounts and information.

**Fields:**
- `id` (Integer, Primary Key)
- `username` (String, Unique, Not Null)
- `password` (String, Not Null) - Hashed password
- `email` (String, Unique, Not Null)
- `name` (String, Not Null)
- `phone` (String)
- `address` (Text)
- `date_of_birth` (Date)
- `gender` (String)
- `is_active` (Boolean, Default: True)
- `created_at` (DateTime)

**Relationships:**
- One-to-Many with Appointment

### 5. Appointment
Stores appointment records between patients and doctors.

**Fields:**
- `id` (Integer, Primary Key)
- `patient_id` (Integer, Foreign Key → Patient.id, Not Null)
- `doctor_id` (Integer, Foreign Key → Doctor.id, Not Null)
- `date` (Date, Not Null)
- `time` (Time, Not Null)
- `status` (String, Default: 'Booked', Not Null) - Values: 'Booked', 'Completed', 'Cancelled'
- `reason` (Text)
- `created_at` (DateTime)
- `updated_at` (DateTime)

**Relationships:**
- Many-to-One with Patient
- Many-to-One with Doctor
- One-to-One with Treatment

**Notes:**
- Double booking prevention is handled in application logic
- Application checks for existing 'Booked' appointments before creating new ones
- Cancelled appointments free up the time slot for new bookings

### 6. Treatment
Stores treatment records for completed appointments.

**Fields:**
- `id` (Integer, Primary Key)
- `appointment_id` (Integer, Foreign Key → Appointment.id, Unique, Not Null)
- `diagnosis` (Text, Not Null)
- `prescription` (Text)
- `notes` (Text)
- `created_at` (DateTime)
- `updated_at` (DateTime)

**Relationships:**
- One-to-One with Appointment

## Entity Relationships

```
Admin (Independent)
  └─ No relationships

Department
  └─ Has many Doctors

Doctor
  ├─ Belongs to Department (optional)
  └─ Has many Appointments

Patient
  └─ Has many Appointments

Appointment
  ├─ Belongs to Patient
  ├─ Belongs to Doctor
  └─ Has one Treatment (optional)

Treatment
  └─ Belongs to Appointment
```

## Database Initialization

The database is created programmatically using `init_db.py`:
1. Creates all tables
2. Creates predefined Admin user (username: admin, password: admin123)

## Constraints and Validation

- Username uniqueness enforced at database level for Admin, Doctor, and Patient
- Email uniqueness enforced at database level for Admin, Doctor, and Patient
- Double booking prevention handled in application logic (checks for existing 'Booked' appointments)
- Foreign key constraints ensure referential integrity
- Treatment has unique constraint on appointment_id (one treatment per appointment)

## Status Values

**Appointment Status:**
- `Booked`: Appointment is scheduled
- `Completed`: Appointment has been completed and treatment recorded
- `Cancelled`: Appointment has been cancelled

