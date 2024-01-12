from flask import Flask, render_template, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import InputRequired, Length, Email, EqualTo
from flask_bcrypt import Bcrypt
import mysql.connector

app = Flask(__name__)
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'kebAPPka'
#app.config['MYSQL_DATABASE_PORT'] = 3306
app.config['SECRET_KEY'] = 'bardzo_tajny_klucz'

bcrypt = Bcrypt(app)

def get_db_connection():
    return mysql.connector.connect(
        host = app.config['MYSQL_DATABASE_HOST'],
        user = app.config['MYSQL_DATABASE_USER'],
        password = app.config['MYSQL_DATABASE_PASSWORD'],
        database = app.config['MYSQL_DATABASE_DB'],
        #port = app.config['MYSQL_DATABASE_PORT']
    )

def execute_sql_query(sql, values=None, fetchone=False, commit=False):
    #connection = db.engine.connect()
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        if values:
            cursor.execute(sql, values)
        else:
            cursor.execute(sql)

        # Sprawdź, czy zapytanie jest typu SELECT
        if cursor.description:
            if fetchone:
                result = cursor.fetchone()
            else:
                result = cursor.fetchall()
        else:
            result = None

        if commit:
            connection.commit()

        return result
    finally:
        cursor.close()
        connection.close()

def insert_email_verification(email):
    sql = (
        "INSERT INTO email_verification (email, verification_code, code_expiry_time, verification_link, link_expiry_time, created_at)"
        "VALUES (%s, 'dummy_code', NOW(), 'dummy_link', NOW(), NOW())"
    )
    values = (
        email,
    )
    execute_sql_query(sql, values, commit=True)


def insert_user(username, email, phone_number, password, authentication_type, terms_of_service_consent, newsletter_consent, location_processing_consent):
    sql = (
        "INSERT INTO users"
        "(username, email, phone_number, password, authentication_type, terms_of_service_consent, newsletter_consent, location_processing_consent, created_at)"
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())"
    )
    values = (
        username, email, phone_number, password, 
        authentication_type, terms_of_service_consent, 
        newsletter_consent, location_processing_consent
    )
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
