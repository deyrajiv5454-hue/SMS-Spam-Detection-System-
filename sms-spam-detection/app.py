from flask import Flask, render_template, request, redirect, url_for, flash ,session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import pickle
import os
import random
from dotenv import load_dotenv
from flask_mail import Mail, Message

app = Flask(__name__)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'priyanshukumarsaw1@gmail.com'
app.config['MAIL_PASSWORD'] = 'ehuj liqa iesm hqxn'
app.config['MAIL_DEFAULT_SENDER'] = 'priyanshukumarsaw1@gmail.com'

mail = Mail(app)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

# Initialize Extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Load the trained Machine Learning model
model = None
cv = None

try:
    with open('model.pkl', 'rb') as model_file:
        model = pickle.load(model_file)
    with open('vectorizer.pkl', 'rb') as vocab_file:
        cv = pickle.load(vocab_file)
except FileNotFoundError:
    print("Error: model.pkl or vectorizer.pkl not found. Run train_model.py first.")

# --- Database Models ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Routes ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get("email")

        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists. Please choose a different one.')
            return redirect(url_for('register'))
            
        # Hash password and save user
        hashed_pw = generate_password_hash(password)
        new_user = User(username=username, password=hashed_pw, email=email)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! You can now log in.')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):

            otp = str(random.randint(100000, 999999))

            session['otp'] = otp
            session['user_id'] = user.id

            msg = Message(
                subject="OTP Verification",
                recipients=[user.email]
            )

            msg.body = f"""
Hello {user.username},

Your OTP is:

{otp}

Do not share this OTP with anyone.
"""

            mail.send(msg)

            flash("OTP has been sent to your email.")

            return redirect(url_for('verify_otp'))

        else:
            flash("Invalid Username or Password")

    return render_template("login.html")

@app.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():

    if request.method == 'POST':

        entered_otp = request.form.get('otp')

        if entered_otp == session.get('otp'):

            user = User.query.get(session.get('user_id'))

            login_user(user)

            session.pop('otp', None)
            session.pop('user_id', None)

            flash("Login Successful")

            return redirect(url_for('home'))

        else:
            flash("Invalid OTP")

    return render_template("verifyotp.html")

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
 user = User.query.get_or_404(id)
 if request.method == 'POST':
    user.username=request.form.get('username')
    user.email=request.form.get('email')
    user.password=generate_password_hash(request.form.get('password'))
    try:
      db.session.commit()
      return redirect(url_for('login'))
    except Exception as e:
        db.session.rollback()
        return f'error updating{e}'    
 return render_template('update.html', user=user)

@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
    user = User.query.get_or_404(id)
    if request.method == 'POST':
        try:
            db.session.delete(user)
            db.session.commit()
            return redirect(url_for('register'))
        except Exception as e:
            db.session.rollback()
            return f'error deleting user: {e}'
    return render_template('delete.html', user=user)

    
    
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
@login_required
def home():
    prediction = None
    message = ""

    if request.method == 'POST':
        message = request.form.get('message')

        # Check model
        if cv is None or model is None:
            flash("Error: Model not found.")
            return render_template(
                'index.html',
                prediction=None,
                message=message
            )

    if message:
            vect = cv.transform([message]).toarray()
            my_prediction = model.predict(vect)
            prediction = "SPAM" if my_prediction[0] == 1 else "NOT SPAM"

            # Send Email
            msg = Message(
                subject="Spam Detection Result",
                recipients=[current_user.email]
            )

            msg.body = f"""
Hello {current_user.username},

Your Message:
{message}

Prediction Result:
{prediction}

Thank you for using Spam Detector.
"""

            mail.send(msg)

    return render_template(
        "index.html",
        prediction=prediction,
        message=message
    )

# Initialize database tables before running
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    host = os.getenv('HOST')
    app.run(debug=True, host=host)