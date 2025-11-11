# How to Run Hospital Management System Locally

## Quick Start Commands

### 1. Navigate to Project Directory
```bash
cd "D:\Hospital-Management-App---V1-"
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Initialize Database
```bash
python init_db.py
```

### 4. Run the Application
```bash
python app.py
```

### 5. Access the Application
Open your browser and go to:
```
http://localhost:5000
```

## Default Login Credentials

**Admin:**
- Username: `admin`
- Password: `admin123`

## Complete Setup (One-time)

```bash
# Navigate to project
cd "D:\Hospital-Management-App---V1-"

# Install dependencies
pip install -r requirements.txt

# Initialize database (creates admin user)
python init_db.py

# Run the application
python app.py
```

## Daily Usage

After the first setup, you only need to run:
```bash
python app.py
```

## Troubleshooting

### If you get "Module not found" error:
```bash
pip install -r requirements.txt
```

### If you get database errors:
```bash
python init_db.py
```

### If port 5000 is already in use:
Change the port in `app.py` (last line):
```python
app.run(debug=True, port=5001)
```

## Features Available

- ✅ Admin Dashboard with Charts
- ✅ Doctor Dashboard with Charts  
- ✅ Patient Dashboard with Charts
- ✅ API Endpoints (JSON-based)
- ✅ Form Validation (Frontend & Backend)
- ✅ Responsive UI (Mobile, Tablet, PC)
- ✅ Professional Modern Design

## API Endpoints

All API endpoints require authentication (login first):

- `GET /api/doctors` - List all doctors
- `POST /api/doctors` - Create a doctor
- `GET /api/doctors/<id>` - Get a doctor
- `PUT /api/doctors/<id>` - Update a doctor
- `DELETE /api/doctors/<id>` - Delete a doctor

Same pattern for `/api/patients` and `/api/appointments`

## Stopping the Server

Press `Ctrl + C` in the terminal to stop the server.

