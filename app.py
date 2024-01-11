from flask import Flask, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import InputRequired, Length, Email, EqualTo
from flask_bcrypt import Bcrypt
from sqlalchemy import text

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost:3306/kebAPPka'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

def execute_sql_query(sql, values=None, fetchone=False, commit=False):
    connection = db.engine.connect()
    try:
        if values is None:
            result = connection.execute(text(sql))
        elif isinstance(values, (tuple, list)):
            # Handle both a single tuple and a list
            if len(values) == 1:
                result = connection.execute(text(sql), values[0])
            else:
                result = connection.execute(text(sql), *values)
        elif isinstance(values, dict):
            # Use parameter binding here
            result = connection.execute(text(sql), values)
        else:
            raise ValueError("Values must be either a tuple, a list, or a dictionary")

        if commit:
            connection.commit()

        if fetchone:
            return result.fetchone()
    finally:
        connection.close()


def insert_email_verification(email):
    sql = (
        "INSERT INTO email_verification (email, verification_code, code_expiry_time, verification_link, link_expiry_time, created_at)"
        "VALUES (:email, 'dummy_code', NOW(), 'dummy_link', NOW(), NOW())"
    )
    values = {
        'email': email,
    }
    execute_sql_query(sql, values, commit=True)


def insert_user(username, email, phone_number, password, authentication_type, terms_of_service_consent, newsletter_consent, location_processing_consent):
    sql = (
        "INSERT INTO users"
        "(username, email, phone_number, password, authentication_type, terms_of_service_consent, newsletter_consent, location_processing_consent, created_at)"
        "VALUES (:username, :email, :phone_number, :password, :authentication_type, :terms_of_service_consent, :newsletter_consent, :location_processing_consent, NOW())"
    )
    values = {
        'username': username,
        'email': email,
        'phone_number': phone_number,
        'password': password,
        'authentication_type': authentication_type,
        'terms_of_service_consent': terms_of_service_consent,
        'newsletter_consent': newsletter_consent,
        'location_processing_consent': location_processing_consent
    }
    execute_sql_query(sql, values, commit=True)

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[InputRequired(), Length(max=120)])
    phone_number = StringField('Phone Number', validators=[InputRequired(), Length(min=1, max=20)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6, max=60)])
    confirm_password = PasswordField('Confirm Password', validators=[InputRequired(), EqualTo('password', message='Passwords must match')])
    authentication_type = SelectField('Second Authentication Type', choices=[('second_email', 'Support email'), ('phone', 'SMS code'), ('authy_app', 'Authy application')], validators=[InputRequired()])
    terms_of_service_consent = BooleanField('I accept the Terms of Service.')
    newsletter_consent = BooleanField('I want to receive the Newsletter.')
    location_processing_consent = BooleanField('I consent to the processing of my location data to find the nearest kebab places.')
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6, max=60)])
    submit = SubmitField('Log In')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        insert_email_verification(form.email.data)

        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        insert_user(
            form.username.data,
            form.email.data,
            form.phone_number.data,
            hashed_password,
            form.authentication_type.data,
            form.terms_of_service_consent.data,
            form.newsletter_consent.data,
            form.location_processing_consent.data
        )
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('index'))

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        # Logic for handling login, check if the user exists and the password is correct
        flash('Login successful!', 'success')
        return redirect(url_for('index'))

    return render_template('login.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)
