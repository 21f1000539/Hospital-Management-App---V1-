from flask import Flask
from database import db
from models import Admin, Doctor, Patient, Department, Appointment, Treatment

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital_management.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize db with app
db.init_app(app)

@app.route('/')
def index():
    return '<h1>Hospital Management System</h1><p>Database setup complete. Use init_db.py to initialize the database.</p>'

if __name__ == '__main__':
    app.run(debug=True)

