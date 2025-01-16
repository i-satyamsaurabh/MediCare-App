from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify,abort
from flask_sqlalchemy import SQLAlchemy
import random
from flask_mail import Mail, Message
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from datetime import datetime, timedelta, timezone
import re
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
import os
from werkzeug.utils import secure_filename
from sqlalchemy.orm import joinedload

from threading import Timer
from flask import current_app

from flask import jsonify
from twilio.rest import Client
from flask_mail import Message
import os
import json

# Twilio and Flask-Mail configuration
TWILIO_ACCOUNT_SID = 'ACca3f42586f99c20b99eca49b01af6e7d'
TWILIO_AUTH_TOKEN = '61d4f7e3280e4adf9247d9dbff2c871f'
TWILIO_PHONE_NUMBER = '+17753059672'
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


from model import db, Patient, Doctor, Appointment, Department, Rating, Notification, Prescription

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(150), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    doctor = db.relationship('Doctor', back_populates='user', uselist=False, cascade='all, delete-orphan')
    patient = db.relationship('Patient', back_populates='user', uselist=False, cascade='all, delete-orphan')




# App Configuration
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'

# Flask-Mail Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'medicare.services.team@gmail.com'
app.config['MAIL_PASSWORD'] = 'ulhf mvmg jbmf uzwx'
app.config['MAIL_DEFAULT_SENDER'] = 'medicare.services.team@gmail.com'



# Add these configurations to your app
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'static', 'doctor_images')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

mail = Mail(app)

# Sample dataset of conditions and their symptoms
CONDITIONS = {
    "Flu": ["fever", "headache", "fatigue", "cough"],
    "Common Cold": ["sneezing", "runny nose", "sore throat", "cough"],
    "Migraine": ["headache", "nausea", "sensitivity to light", "blurred vision"],
    "COVID-19": ["fever", "dry cough", "fatigue", "loss of taste or smell"],
    "Pneumonia": ["cough", "fever", "chills", "sore throat"],
    "Asthma": ["chest pain", "shortness of breath", "wheezing", "cough"],
    "Diabetes": ["fever", "weight loss", "polyuria", "polydipsia"],
    "Heart Disease": ["chest pain", "shortness of breath", "fatigue", "dizziness"],
    "Stomach Ache": ["nausea", "vomiting", "abdominal pain", "diarrhea"],
    "Allergic Reaction": ["skin rash", "hives", "itching", "swelling"],
    "Gallbladder Disease": ["nausea", "vomiting", "abdominal pain", "nausea"],
    "Sinusitis": ["headache", "sneezing", "runny nose", "sore throat"],
    "Bronchitis": ["cough", "sneezing", "shortness of breath", "wheezing"],
    "Food Poisoning": ["nausea", "vomiting", "diarrhea", "stomach cramps"]
}

departments = [
    "Cardiology",
    "Neurology",
    "ENT (General)",
    "Gastroenterology",
    "Pediatrics",
    "Orthopedics",
    "Dermatology",
    "Urology",
    "Gynecology",
    "Psychiatry",
    "Dentistry",
    "Other",
]

def insert_departments():
    with app.app_context():  # Use the Flask app context
        for department_name in departments:
            # Check if department already exists
            existing_department = Department.query.filter_by(name=department_name).first()
            if not existing_department:
                new_department = Department(name=department_name)
                db.session.add(new_department)
        db.session.commit()
        print("Departments inserted successfully!")


db.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'warning'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        next_page = request.args.get('next')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user)
                print(f"User logged in: {user.id}, Doctor: {user.doctor}, Patient: {user.patient}")
                if user.doctor:
                    return redirect(next_page or url_for('doctor'))
                elif user.patient:
                    return redirect(next_page or url_for('user'))
                else:
                    return redirect(next_page or url_for('index'))
            else:
                flash('Invalid password.', 'danger')
        else:
            flash('Invalid email address.', 'danger')

    return render_template('login.html')



@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))

@app.route('/register_patient', methods=['GET', 'POST'])
def register_patient():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        mobile = request.form.get('mobile')
        password = request.form.get('password')
        city = request.form.get('city')
        emergency_email = request.form.get('emergency_email')
        emergency_number = request.form.get('emergency_number')
        gender = request.form.get('gender')
        age = request.form.get('age')

        print(f"Name: {name}, Email: {email}, Mobile: {mobile}, Password: {password}, City: {city}, Emergency Email: {emergency_email}, Emergency Number: {emergency_number}, Gender: {gender}, Age: {age}")

        # Check if password is provided
        if not password:
            flash('Password is required.', 'danger')
            return redirect(url_for('register_patient'))

        # Password validation
        password_pattern = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@+$!%*?&])[A-Za-z\d@+$!%*?&]{8,}$"
        if not re.match(password_pattern, password):
            flash('Password must include at least 8 characters, uppercase and lowercase letters, a number, and a special character.', 'danger')
            return redirect(url_for('register_patient'))

        # Check if email already exists in User table
        if User.query.filter_by(email=email).first():
            flash('Email already exists. Please login or use a different email.', 'danger')
            return redirect(url_for('register_patient'))

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Create a new User record
        new_user = User(
            name=name,
            email=email,
            password=hashed_password,
            city=city
        )
        db.session.add(new_user)
        db.session.commit()  # Commit to generate the user_id

        # Use the new user's ID for the Patient record
        new_patient = Patient(
            user_id=new_user.id,
            name=name,
            email=email,
            mobile=mobile,
            password=hashed_password,
            city=city,
            emergency_email=emergency_email,
            emergency_number=emergency_number,
            gender=gender,
            age=int(age) if age else None
        )
        db.session.add(new_patient)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register_patient.html')


@app.route('/register_doctor', methods=['GET', 'POST'])
def register_doctor():
    departments = Department.query.all()
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        city = request.form.get('city')
        department_id = request.form.get('specialization')
        experience = request.form.get('experience')
        description = request.form.get('description')


        selected_department = Department.query.get(department_id)
        specialization = selected_department.name

        
        # Handle image file
        image_filename = None
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Add timestamp to filename to make it unique
                filename = f"{int(time.time())}_{filename}"
                # Create upload folder if it doesn't exist
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                # Save the file
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_filename = filename
            elif file.filename:  # If file was provided but invalid type
                flash('Invalid file type. Please upload PNG, JPG, JPEG, or GIF files only.', 'danger')
                return redirect(url_for('register_doctor',) )

        # Password validation
        password_pattern = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@+$!%*?&])[A-Za-z\d@+$!%*?&]{8,}$"
        if not re.match(password_pattern, password):
            flash('Password must include at least 8 characters, uppercase and lowercase letters, a number, and a special character.', 'danger')
            return redirect(url_for('register_doctor'))

        # Check if email already exists in User table
        if User.query.filter_by(email=email).first():
            flash('Email already exists. Please login or use a different email.', 'danger')
            return redirect(url_for('register_doctor'))

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Create a new User record
        new_user = User(
            name=name,
            email=email,
            password=hashed_password,
            city=city
        )
        db.session.add(new_user)
        db.session.commit()  # Commit to generate the user_id

        # Create a new Doctor record and associate it with the new User record
        new_doctor = Doctor(
            user_id=new_user.id,  # Associate with the User record
            name=name,
            email=email,
            password=hashed_password,
            city=city,
            specialization=specialization,
            department_id=department_id,
            experience=experience,
            description=description,
            image=image_filename  # Add the image filename
        )
        db.session.add(new_doctor)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register_doctor.html', departments=departments)

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        if email:
            otp = str(random.randint(1000, 9999))
            session['otp'] = otp
            session['email'] = email

            msg = Message(
                'Reset Password Code',
                sender='satyam2011wc@gmail.com',
                recipients=[email]
            )
            # HTML content with inline styling
            msg.html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{
                        font-family: Libre Baskerville, serif;
                        background-color: #f9f9f9;
                        margin: 0;
                        padding: 0;
                    }}
                    .email-container {{
                        background-color: #ffffff;
                        padding: 20px;
                        margin: 10px auto;
                        border: 1px solid rgb(5, 4, 4);
                        border-radius: 10px;
                        width: 80%;
                        max-width: 500px;
                    }}
                    .email-header {{
                        font-size: 18px;
                        font-weight: bold;
                        color:rgb(6, 16, 71);
                        margin-bottom: 20px;
                    }}
                    .email-content {{
                        font-size: 16px;
                        color: #555555;
                        line-height: 1.5;
                    }}
                    .email-footer {{
                        font-size: 14px;
                        color: #999999;
                        margin-top: 20px;
                    }}
                </style>
            </head>
            <body>
                <div class="email-container">
                    <div class="email-header">Reset Your Password</div>
                    <div class="email-content">
                        Hello,<br><br>
                        Your password reset code is <strong>{otp}</strong>.<br>
                        Please enter this code to proceed with resetting your password.<br><br>
                        If you didn’t request this, please ignore this message.
                    </div>
                    <div class="email-footer">
                        Thank you,<br>
                        Medicare Health 
                    </div>
                </div>
            </body>
            </html>
            """
            mail.send(msg)

            flash('OTP sent to your email!', 'success')
            return redirect(url_for('reset_password'))
        else:
            flash('Please enter a valid email address!', 'danger')
    return render_template('forgot_password.html')


@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        entered_otp = request.form.get('otp')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        # Ensure session variables exist
        if 'otp' not in session or 'email' not in session:
            flash('Session expired or invalid request. Please try again.', 'danger')
            return redirect(url_for('forgot_password'))

        # Validate OTP
        if entered_otp == session['otp']:
            # Validate passwords
            if new_password == confirm_password:
                if len(new_password) >= 8 and re.search(r'[A-Z]', new_password) and re.search(r'[0-9]', new_password):
                    # Find user by email
                    email = session.get('email')
                    user = User.query.filter_by(email=email).first()
                    if user:
                        # Update password
                        user.password = generate_password_hash(new_password)
                        db.session.commit()

                        # Clear session variables
                        session.pop('otp', None)
                        session.pop('email', None)

                        flash('Password reset successfully! Please log in.', 'success')
                        return redirect(url_for('login'))
                    else:
                        flash('User not found!', 'danger')
                else:
                    flash('Password must be at least 8 characters long and include an uppercase letter and a number.', 'danger')
            else:
                flash('Passwords do not match!', 'danger')
        else:
            flash('Invalid OTP!', 'danger')

        # Clear OTP on failure for security
        session.pop('otp', None)

    return render_template('reset_password.html')   


def update_appointment_status(appointment):
    """
    Updates the status of an appointment based on its date and time
    compared to the current datetime.
    """
    current_datetime = datetime.now()
    appointment_datetime = datetime.combine(appointment.appointment_date, appointment.appointment_time)
    
    if current_datetime > appointment_datetime:
        appointment.status = 'completed'
        return True
    return False

def update_all_appointments_status():
    """
    Updates status for all appointments in the database.
    Returns the number of appointments updated.
    """
    appointments = Appointment.query.all()
    updated_count = 0
    
    for appointment in appointments:
        if update_appointment_status(appointment):
            updated_count += 1
    
    if updated_count > 0:
        db.session.commit()
    
    return updated_count



@app.route('/get_doctors/<int:department_id>', methods=['GET'])
def get_doctors(department_id):
    doctors = Doctor.query.filter_by(department_id=department_id).all()
    doctor_data = [{"id": doctor.id, "name": doctor.name} for doctor in doctors]
    return jsonify(doctor_data)


def get_user_appointments():
    # First update the status of all appointments
    update_all_appointments_status()
    
    # Then fetch the appointments
    appointments = (
        Appointment.query.filter_by(patient_id=current_user.id)
        .order_by(Appointment.appointment_date.desc(), Appointment.appointment_time.desc())
        .limit(3)
        .all()
    )
    
    formatted_appointments = []
    for appt in appointments:
        formatted_appointments.append({
            'id': appt.id,
            'doctor_name': appt.doctor.name,
            'specialization': appt.doctor.specialization,
            'date': appt.appointment_date,
            'time': appt.appointment_time,
            'status': appt.status  # Now using the updated status from database
        })
    
    return formatted_appointments



@app.route('/delete_appointment/<int:appointment_id>', methods=['POST', 'GET'])
def delete_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    db.session.delete(appointment)
    db.session.commit()
    return redirect(url_for('user'))



@app.route('/edit_appointment/<int:appointment_id>', methods=['GET', 'POST'])
def edit_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    
    if request.method == 'POST':
        # Convert the string date to a datetime object
        appointment_date_str = request.form.get('appointment_date')
        appointment_time_str = request.form.get('appointment_time')
        
        # Parse the date string into a datetime object
        appointment_date = datetime.strptime(appointment_date_str, '%Y-%m-%d').date()
        # Parse the time string into a datetime object (using a dummy date)
        appointment_time = datetime.strptime(appointment_time_str, '%H:%M').time()

        # Update the appointment's date and time
        appointment.appointment_date = appointment_date
        appointment.appointment_time = appointment_time
        
        db.session.commit()
        return redirect(url_for('user'))
    
    return render_template('edit_appointment.html', appointment=appointment)


@app.route('/rate_appointment/<int:appointment_id>', methods=['GET', 'POST'])
def rate_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)

    if request.method == 'POST':
        data = request.form
        rating_value = data.get('rating')

        if not rating_value:
            return jsonify({'error': 'Rating value is required.'}), 400

        # Check if a rating already exists
        if Rating.query.filter_by(appointment_id=appointment_id).first():
            flash('You have already rated this appointment.', 'danger')
            return redirect(url_for('rate_appointment', appointment_id=appointment_id))

        # Save the new rating
        new_rating = Rating(
            appointment_id=appointment_id,
            rating=float(rating_value),
        )
        db.session.add(new_rating)

        # Update the doctor's average rating
        doctor_id = appointment.doctor_id
        all_ratings = Rating.query.join(Appointment).filter(Appointment.doctor_id == doctor_id).all()
        average_rating = sum(r.rating for r in all_ratings) / len(all_ratings)

        # Update the doctor's rating
        doctor = Doctor.query.get(doctor_id)
        doctor.rating = round(average_rating, 1)  # Optional: round to one decimal
        db.session.commit()

        flash('Rating saved successfully!', 'danger')
        return redirect(url_for('rate_appointment', appointment_id=appointment_id))

    return render_template('rate_appointment.html', appointment=appointment)



@app.route('/user')
@login_required
def user():
    user = User.query.all()
    patients = Patient.query.all()
    doctors = Doctor.query.all()
    departments = Department.query.all()
    appointments = get_user_appointments()

    # Attach prescriptions to each appointment dictionary
    for appointment in appointments:
        appointment_id = appointment.get('id')  # Extract id from the dictionary
        if appointment_id:
            appointment['prescriptions'] = Prescription.query.filter_by(appointment_id=appointment_id).all()
    
    return render_template(
        'user.html',
        user=user,
        patients=patients,
        doctors=doctors,
        departments=departments,
        appointments=appointments,
        datetime=datetime
    )


@app.route('/symptom-checker', methods=['POST'])
def symptom_checker():
    # Retrieve user input
    symptoms_input = request.form.get('symptoms', '').strip().lower()
    
    if not symptoms_input:
        return jsonify({
            'flash': {
                'category': 'danger',
                'message': 'Please enter some symptoms.'
            }
        })

    # Split input symptoms into a list
    user_symptoms = [symptom.strip() for symptom in symptoms_input.split(',') if symptom.strip()]

    if not user_symptoms:
        return jsonify({
            'flash': {
                'category': 'danger',
                'message': 'Invalid input format. Please enter symptoms separated by commas.'
            }
        })

    # Match symptoms to conditions
    matches = {}
    for condition, condition_symptoms in CONDITIONS.items():
        matching_symptoms = set(user_symptoms) & set(condition_symptoms)
        if matching_symptoms:
            matches[condition] = len(matching_symptoms)

    # Sort conditions by the number of matching symptoms
    sorted_matches = sorted(matches.items(), key=lambda x: x[1], reverse=True)

    # Generate results for display
    results = [
        {
            "condition": condition,
            "match_count": count,
            "total_symptoms": len(CONDITIONS[condition]),
            "matching_symptoms": list(set(user_symptoms) & set(CONDITIONS[condition]))
        }
        for condition, count in sorted_matches
    ]

    if not results:
        return jsonify({
            'flash': {
                'category': 'warning',
                'message': 'No conditions matched your symptoms. Please consult a medical professional.'
            }
        })

    return jsonify({'results': results})



@app.route('/book_appointment', methods=['POST'])
def book_appointment():
    if request.method == 'POST':
        doctor_id = request.form['doctor']
        date_str = request.form['date']
        time_str = request.form['time']
        
        appointment_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        appointment_time = datetime.strptime(time_str, '%H:%M').time()
        
        # Determine the appointment status
        today = datetime.utcnow().date()
        if appointment_date < today:
            status = 'completed'
        elif appointment_date > today:
            status = 'upcoming'
        else:
            status = 'upcoming'
        
        new_appointment = Appointment(
            patient_id=current_user.id,
            doctor_id=doctor_id,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            status=status
        )
        
        
    # Create a notification for the doctor
        notification_message = f"New appointment with {current_user.name}."
        new_notification = Notification(doctor_id=doctor_id, message=notification_message)
        db.session.add(new_notification)
        db.session.commit()

        db.session.add(new_appointment)
        db.session.commit()
        
        # Fetch the patient's email
        patient_email = current_user.email
        
        # Schedule the email to be sent after 10 seconds
        timer = Timer(10.0, send_confirmation_email_with_app_context, 
                     args=[patient_email, appointment_date, appointment_time, current_user.id, app])
        timer.start()
        
        flash('Appointment booked successfully!', 'appointment')
        return redirect(url_for('user'))

def send_confirmation_email_with_app_context(patient_email, appointment_date, appointment_time, user_id, app):
    with app.app_context():
        # Fetch the most recent appointment for the patient from the database
        latest_appointment = Appointment.query.filter_by(patient_id=user_id)\
                                           .order_by(Appointment.appointment_date.desc()).first()
        
        # Create a new message
        msg = Message('Your Appointment is Booked!',
                      recipients=[patient_email])
        
        # Email body content (in HTML format)
        msg.html = f'''
        <html>
        <body>
            <h3>Dear Patient,</h3>
            <p>Your appointment has been successfully booked with our doctor.</p>
            <p><b>Appointment Details:</b></p>
            <ul>
                <li>Appointment Date: {appointment_date.strftime('%B %d, %Y')}</li>
                <li>Appointment Time: {appointment_time.strftime('%I:%M %p')}</li>
                <li>Doctor: {latest_appointment.doctor.name}</li>
                <li>Department: {latest_appointment.doctor.specialization}</li>
            </ul>
            <p>Please join the Google Meet link at your scheduled time:</p>
            <p><a href="https://meet.google.com/ryg-pqgi-fmn">Join Google Meet</a></p>
            <p>Thank you for choosing MediCare. We look forward to seeing you.</p>
            <p>Best regards,<br>The MediCare Team</p>
        </body>
        </html>
        '''
        
        # Send the email
        mail.send(msg)


from datetime import datetime

@app.route('/doctor')
def doctor():
    doctor = Doctor.query.get_or_404(current_user.doctor.id)
    doctor_id = current_user.doctor.id
    
    # Update appointment statuses before displaying
    update_all_appointments_status()
    
    notifications = Notification.query.filter_by(doctor_id=doctor_id).all()
    unread_notifications = Notification.query.filter_by(doctor_id=doctor_id, is_read=False).count()
    start_date = datetime.now().date()
    end_date = start_date + timedelta(days=7)

    appointments = (
        Appointment.query
        .filter_by(doctor_id=doctor_id)
        .order_by(Appointment.id.desc())
        .all()
    )
    
    today_appointments = (
        Appointment.query
        .filter_by(doctor_id=doctor_id, appointment_date=datetime.now().date())
        .order_by(Appointment.id.desc())
        .count()
    )

    upcoming_appointments = (
        Appointment.query
        .filter(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date >= start_date,
            Appointment.appointment_date <= end_date
        )
        .order_by(Appointment.id.desc())
        .count()
    )

    patient = Patient.query.join(Appointment).filter(Appointment.doctor_id == current_user.doctor.id).all()

    return render_template('doctor.html', 
                         doctor=doctor, 
                         appointments=appointments, 
                         patient=patient, 
                         datetime=datetime, 
                         notifications=notifications, 
                         unread_notifications=unread_notifications, 
                         today_appointments=today_appointments, 
                         upcoming_appointments=upcoming_appointments)

@app.route('/create_appointment', methods=['POST'])
def create_appointment():
    # Extract appointment details from form
    doctor_id = request.form['doctor_id']
    patient_name = request.form['patient_name']
    # Other appointment data...

    # Save appointment to the database
    new_appointment = Appointment(doctor_id=doctor_id, patient_name=patient_name)
    db.session.add(new_appointment)
    db.session.commit()

    # Create a notification for the doctor
    notification_message = f"New appointment with {patient_name}."
    new_notification = Notification(doctor_id=doctor_id, message=notification_message)
    db.session.add(new_notification)
    db.session.commit()

    return redirect(url_for('doctor'))  

@app.route('/notifications')
def notifications():
    # Assuming `current_user` is the logged-in doctor
    doctor_notifications = Notification.query.filter_by(doctor_id=current_user.id).all()
    return render_template('notifications.html', notifications=doctor_notifications)


@app.route('/mark_as_read/<int:notification_id>')
def mark_as_read(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    if notification.doctor_id != current_user.id:
        abort(403)  # Prevent unauthorized access
    notification.is_read = True
    db.session.commit()
    return redirect('/notifications')


@app.context_processor
def inject_notification_count():
    if current_user.is_authenticated:
        unread_count = Notification.query.filter_by(doctor_id=current_user.id, is_read=False).count()
        return {'unread_count': unread_count}
    return {'unread_count': 0}


from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse

@app.route('/emergency', methods=['POST'])
def emergency():
    try:
        # Retrieve emergency contact details
        emergency_phone = current_user.patient.mobile
        emergency_email = current_user.patient.email

        # Ensure phone number has a country code
        country_code = "+91"  # Replace with your country's code
        if not emergency_phone.startswith('+'):
            emergency_phone = country_code + emergency_phone

        # Log the phone number for debugging
        print(f"Calling emergency contact: {emergency_phone}")

        # Create a voice response for the call
        response = VoiceResponse()
        response.say("Hello, This is an emergency alert from the MediCare Platform.", voice='alice')
        response.pause(length=2)
        response.say("The user associated with this number has triggered an emergency alert. Immediate attention is required. It may be a life-threatening situation. ", voice='alice')
        response.pause(length=2)
        response.say("Please check their location and contact them as soon as possible. Thank you.", voice='alice')

        # Make a voice call via Twilio
        call = client.calls.create(
            twiml=str(response),
            from_=TWILIO_PHONE_NUMBER,
            to=emergency_phone
        )

        # Send an email alert via Flask-Mail
        msg = Message(
            "🚨 Emergency Alert: Immediate Attention Required",
            sender=app.config['MAIL_USERNAME'],
            recipients=[emergency_email]
        )
        msg.body = (
            "Dear Emergency Contact,\n\n"
            "This is an automated emergency alert from the MediCare Platform.\n\n"
            "The user associated with this email has triggered an emergency alert. Please take the following actions immediately:\n"
            "- Attempt to contact the user at their registered phone number.\n"
            "- Check on their well-being and provide assistance as needed.\n\n"
            "Details:\n"
            f"- Phone Number: {emergency_phone}\n"
            f"- Email Address: {emergency_email}\n\n"
            "If you have any questions or need further support, please contact our support team.\n\n"
            "Stay Safe,\n"
            "The MediCare Team"
        )
        mail.send(msg)

        return jsonify({"success": True, "message": "Emergency alert sent via call and email!"}), 200

    except Exception as e:
        # Log the error for debugging
        print(f"Error occurred: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/create_prescription/<int:appointment_id>', methods=['GET', 'POST'])
def create_prescription(appointment_id):
    # Fetch the appointment
    appointment = Appointment.query.get_or_404(appointment_id)

    if request.method == 'POST':
        diagnosis = request.form.get('diagnosis')
        medicines = request.form.getlist('medicine[]')  # Expecting multiple inputs
        dosages = request.form.getlist('dosage[]')
        frequencies = request.form.getlist('frequency[]')
        durations = request.form.getlist('duration[]')
        instructions = request.form.get('instructions')

        # Combine medicine details into a list of dictionaries
        medicine_details = [
            {"medicine": med, "dosage": dose, "frequency": freq, "duration": dur}
            for med, dose, freq, dur in zip(medicines, dosages, frequencies, durations)
        ]

        # Create a new Prescription instance
        new_prescription = Prescription(
            appointment_id=appointment_id,
            diagnosis=diagnosis,
            medicines=json.dumps(medicine_details),  # Convert to JSON string
            instructions=instructions,
            created_at=datetime.utcnow()
        )

        # Save to the database
        db.session.add(new_prescription)
        db.session.commit()
        return redirect(url_for('view_prescription', id=new_prescription.id))

    return render_template('create_prescription.html', appointment=appointment)


@app.route('/view_prescription/<int:appointment_id>', methods=['GET', 'POST'])
def view_prescription(appointment_id):
    prescription = Prescription.query.filter_by(appointment_id=appointment_id).first_or_404()
    medicines = json.loads(prescription.medicines)  # Parse JSON string to Python list of dictionaries
    return render_template(
        'view_prescription.html',
        prescription={
            'diagnosis': prescription.diagnosis,
            'instructions': prescription.instructions,
            'created_at': prescription.created_at,
            'medicines': medicines,
            'appointment': prescription.appointment,
        }
    )




@app.route('/find_doctors')
@login_required
def find_doctors():
    # Get the selected department/specialization from query parameters
    selected_dept = request.args.get('specialization', type=int)
    
    # Query doctors based on selection
    if selected_dept:
        doctors = Doctor.query.filter_by(
            department_id=selected_dept,
        ).order_by(Doctor.rating.desc()).all()
    else:
        doctors = Doctor.query.filter_by(
            is_approved=True
        ).order_by(Doctor.rating.desc()).limit(5).all()
    
    # Get all departments for the dropdown
    departments = Department.query.all()
    
    return render_template(
        'user.html',  # your template name
        doctors=doctors,
        departments=departments,
        selected_dept=selected_dept,
        datetime=datetime
    )


@app.route('/api/search_doctors')
@login_required
def search_doctors():
    selected_dept = request.args.get('specialization', type=int)
    
    if selected_dept:
        doctors = Doctor.query.filter_by(
            department_id=selected_dept,
        ).order_by(Doctor.rating.desc()).all()
    else:
        doctors = Doctor.query.order_by(Doctor.rating.desc()).limit(5).all()
    
    doctors_list = [{
        'name': doctor.name,
        'specialization': doctor.specialization,
        'experience': doctor.experience,
        'rating': doctor.rating,
        'image': doctor.image if doctor.image else url_for('static', filename='default_doctor.jpg')
    } for doctor in doctors]
    
    return jsonify({'doctors': doctors_list})

@app.route('/dashboard')
@login_required
def dashboard():
    departments = Department.query.all()
    appointments = Appointment.query.filter_by(patient_id=current_user.id).all()
    
    # Get top rated doctors for initial display
    doctors = Doctor.query.order_by(Doctor.rating.desc()).limit(5).all()
    
    return render_template(
        'user.html',
        departments=departments,
        doctors=doctors,
        appointments=appointments,
        datetime=datetime
    )


@app.route('/private_checkup')
@login_required
def private_checkup():
    # Check if there's a patient profile for the current user
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    
    if not patient:
        flash('Please complete your patient profile first.', 'warning')
        return redirect(url_for('user'))
    
    # Check age restriction (13-29 years)
    if not (13 <= patient.age <= 29):
        flash('This service is only available for patients between 13 and 29 years old.', 'warning')
        return redirect(url_for('user'))
    
    # Get departments related to private checkup
    private_departments = ['Gynecology', 'Andrology', 'Sexual Health', 'Reproductive Health']
    
    # Query doctors from specific departments
    doctors = (Doctor.query
              .join(Department)
              .filter(
                  Department.name.in_(private_departments),
              )
              .all())
    
    return render_template(
        'private_checkup.html',
        doctors=doctors,
        patient=patient
    )



if __name__ == '__main__':
    insert_departments()
    app.run(debug=True)
