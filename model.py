from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin

db = SQLAlchemy()

class Patient(UserMixin, db.Model):
    __tablename__ = 'patient'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    mobile = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    emergency_email = db.Column(db.String(120), nullable=False)
    emergency_number = db.Column(db.String(20), nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship('User', back_populates='patient')
    appointments = db.relationship('Appointment', back_populates='patient')


class Doctor(db.Model):
    __tablename__ = 'doctor'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    specialization = db.Column(db.String(120), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    experience = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    image = db.Column(db.String(255))
    rating = db.Column(db.Float, default=0.0)
    is_approved = db.Column(db.Boolean, default=False)
    description = db.Column(db.Text)

    user = db.relationship('User', back_populates='doctor')
    appointments = db.relationship('Appointment', back_populates='doctor')
    department = db.relationship('Department', back_populates='doctors')



class Department(db.Model):
    __tablename__ = 'department'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Primary key
    name = db.Column(db.String(100), nullable=False, unique=True)    # Department name

    doctors = db.relationship(
        'Doctor',
        back_populates='department',
        foreign_keys='Doctor.department_id', 
    )

    def __repr__(self):
        return f'<Department {self.name}>'



class Appointment(db.Model):
    __tablename__ = 'appointment'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.user_id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    appointment_date = db.Column(db.Date, nullable=False)
    appointment_time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, cancelled, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    patient = db.relationship('Patient', back_populates='appointments')
    doctor = db.relationship('Doctor', back_populates='appointments')
    rating = db.relationship('Rating', uselist=False, back_populates='appointment', cascade="all, delete-orphan")
    prescription = db.relationship('Prescription', uselist=False, back_populates='appointment', cascade="all, delete-orphan")




class Rating(db.Model):
    __tablename__ = 'rating'
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'), nullable=False)
    rating = db.Column(db.Float, default=0.0, nullable=False)  
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship to Appointment
    appointment = db.relationship('Appointment', back_populates='rating')

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Prescription(db.Model):
    __tablename__ = 'prescription'
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'), nullable=False)
    diagnosis = db.Column(db.String(200), nullable=False)
    medicines = db.Column(db.Text, nullable=False)  # JSON string
    dosage = db.Column(db.Text, nullable=True)
    frequency = db.Column(db.Text, nullable=True)
    duration = db.Column(db.Text, nullable=True)
    instructions = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    appointment = db.relationship('Appointment', back_populates='prescription')
