from flask import Flask, render_template, redirect, url_for, flash
from forms import RegistrationForm, LoginForm
from helpers import get_db_connection, execute_sql_query, insert_email_verification, insert_user
from helpers import is_username_available, is_email_available, is_phone_number_available
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'kebAPPka'
app.config['MYSQL_DATABASE_PORT'] = 3306
app.config['SECRET_KEY'] = 'bardzo_tajny_klucz'

bcrypt = Bcrypt(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        if not is_username_available(form.username.data):
            flash('Username is already taken. Please choose another one.', 'danger')
            return render_template('register.html', form=form)

        if not is_email_available(form.email.data):
            flash('Email is already registered. Please use a different email.', 'danger')
            return render_template('register.html', form=form)

        if not is_phone_number_available(form.phone_number.data):
            flash('Phone number is already registered. Please use a different phone number.', 'danger')
            return render_template('register.html', form=form)

        print("Before insert_user")

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

        print("After insert_user")

        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('index'))

    print(form.username.errors)
    print(form.email.errors)
    print(form.phone_number.errors)

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
