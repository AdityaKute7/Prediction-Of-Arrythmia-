from flask import Flask, request, render_template, redirect, url_for, session, jsonify, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
import numpy as np
from werkzeug.security import generate_password_hash, check_password_hash
import joblib
from sklearn.preprocessing import LabelEncoder

# Load the Random Forest model and LabelEncoder
model = joblib.load('C:/Users/ASUS/Downloads/wetransfer_arrythmia_2025-01-31_0904/wetransfer_arrythmia_2025-01-31_0904/ARRYTHMIA/ecg_rf_model.pkl')
label_encoder = joblib.load('C:/Users/ASUS/Downloads/wetransfer_arrythmia_2025-01-31_0904/wetransfer_arrythmia_2025-01-31_0904/ARRYTHMIA/label_encoder.pkl')

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure secret key

# Set up Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Set up SQLite with SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the User model with security questions
class User(UserMixin, db.Model):
    id = db.Column(db.String(80), primary_key=True)
    password = db.Column(db.String(120), nullable=False)
    answer_1 = db.Column(db.String(120), nullable=False)
    answer_2 = db.Column(db.String(120), nullable=False)

    @property
    def is_active(self):
        return True

# Create the database tables
with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# Function to predict ECG
def predict_ecg(ecg_values):
    ecg_values = np.array(ecg_values).reshape(1, -1)
    prediction = model.predict(ecg_values)
    decoded_prediction = label_encoder.inverse_transform(prediction)
    return decoded_prediction[0]

@app.route('/')
def home():
    return redirect(url_for('arrhythmia_info'))

@app.route('/dashboard')
@login_required
def index():
    if 'questions_answered' not in session or not session['questions_answered']:
        return redirect(url_for('questions'))
    return render_template('index.html')

@app.route('/questions', methods=['GET', 'POST'])
@login_required
def questions():
    if request.method == 'POST':
        symptoms = {
            'chest_pain': request.form.get('chest_pain', '0'),
            'shortness_of_breath': request.form.get('shortness_of_breath', '0'),
            'fatigue': request.form.get('fatigue', '0'),
            'dizziness': request.form.get('dizziness', '0'),
            'palpitations': request.form.get('palpitations', '0')
        }
        session['symptoms'] = symptoms
        session['questions_answered'] = True
        return redirect(url_for('index'))

    return render_template('questions.html')

@app.route('/predict', methods=['POST'])
@login_required
def predict():
    try:
        data = request.get_json()
        ecg_values = [
            float(data.get('rr_interval', 0)),
            float(data.get('p_wave', 0)),
            float(data.get('qrs_complex', 0)),
            float(data.get('t_wave', 0)),
            float(data.get('qt_interval', 0))
        ]

        if not all(ecg_values):
            return jsonify({'error': 'Please provide all necessary inputs.'}), 400

        ecg_result = predict_ecg(ecg_values)
        symptoms = session.get('symptoms', {})
        yes_count = list(symptoms.values()).count('1')

        # Suggestion logic
        if yes_count >= 3:
            suggestion = "High risk of underlying health problems. Consult a healthcare provider."
        elif yes_count == 2:
            suggestion = "Monitor symptoms. Consult a doctor if they persist."
        elif yes_count == 1:
            suggestion = "Symptoms seem mild. Maintain a healthy lifestyle."
        elif all(value == '0' for value in symptoms.values()) and ecg_result == 'Normal':
            suggestion = "You are healthy."
        elif all(value == '0' for value in symptoms.values()) and ecg_result == 'Arrhythmia':
            suggestion = "Visit a physician promptly."
        else:
            suggestion = "Consult a healthcare provider for evaluation."

        # Result logic
        result = ecg_result
        cure = "" if result == 'Normal' else "Consult a cardiologist for treatment."
        precautions = "Maintain a healthy lifestyle." if result == 'Normal' else "Stay active, avoid smoking, and manage stress."

        return render_template('result.html', ecg_result=result, cure=cure, precautions=precautions, suggestion=suggestion)

    except Exception as e:
        return jsonify({'error': f"An error occurred: {str(e)}"}), 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.get(username)

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        flash('Invalid credentials. Please try again.', 'error')
    return render_template('login.html')

@app.route('/info')
def arrhythmia_info():
    return render_template('arrhythmia_info.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('questions_answered', None)
    session.pop('symptoms', None)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        answer_1 = request.form['answer_1']
        answer_2 = request.form['answer_2']

        if User.query.get(username):
            flash('Username already exists. Please choose a different one.', 'error')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(id=username, password=hashed_password, answer_1=answer_1, answer_2=answer_2)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        username = request.form['username']
        answer_1 = request.form['answer_1']
        answer_2 = request.form['answer_2']
        user = User.query.get(username)

        if user and user.answer_1 == answer_1 and user.answer_2 == answer_2:
            return redirect(url_for('reset_password', username=username))
        return 'Incorrect answers or username not found.'
    return render_template('forgot_password.html')

@app.route('/reset_password/<username>', methods=['GET', 'POST'])
def reset_password(username):
    if request.method == 'POST':
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        if new_password == confirm_password:
            user = User.query.get(username)
            if user:
                user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
                db.session.commit()
                flash('Password reset successfully.', 'success')
                return redirect(url_for('login'))
            flash('User not found.', 'error')
        else:
            flash('Passwords do not match.', 'error')
    return render_template('reset_password.html', username=username)

if __name__ == '__main__':
    app.run(debug=True)