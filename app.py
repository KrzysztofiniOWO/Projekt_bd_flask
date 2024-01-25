from flask import Flask, render_template, redirect, url_for, flash, session, request
from forms import RegistrationForm, LoginForm
from helpers import execute_sql_query, insert_user, insert_email_verification
from helpers import is_username_available, is_email_available, is_phone_number_available, get_user_data_by_username
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'kebAPPka'
app.config['MYSQL_DATABASE_PORT'] = 3306
app.config['SECRET_KEY'] = 'bardzo_tajny_klucz'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = True

bcrypt = Bcrypt(app)
app.secret_key = 'bardzo_tajny_klucz'

@app.route('/')
def index():
    username = session.get('username')
    return render_template('index.html', username=username)

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
        username = form.username.data
        password = form.password.data

        # Get user data from the database
        user_data = get_user_data_by_username(username)

        if user_data and bcrypt.check_password_hash(user_data['password'], password):
            # Set user session data
            session['username'] = username

            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')

    return render_template('login.html', form=form)

@app.route('/logout', methods=['POST'])
def logout():
    # Usunięcie danych sesji
    session.pop('username', None)

    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/search_by_district', methods=['POST'])
def search_by_district():
    district_name = request.form.get('district')

    sql = "SELECT local_name, description, rating FROM local_accounts WHERE district_id IN (SELECT district_id FROM districts WHERE district = %s)"
    values = (district_name,)
    local_accounts = execute_sql_query(sql, values)

    return render_template('lokale.html', local_accounts=local_accounts, district_name=district_name, username=session.get('username'))

@app.route('/details/<string:lokal_name>')
def details(lokal_name):
    # Pobierz dane o lokalu z bazy danych na podstawie lokal_name
    sql = "SELECT local_name, description, rating FROM local_accounts WHERE local_name = %s"
    values = (lokal_name,)
    lokal_data = execute_sql_query(sql, values, fetchone=True)

    if lokal_data:
        return render_template('szczegoly_lokalu.html', lokal_data=lokal_data, username=session.get('username'))
    else:
        flash('Lokal o podanej nazwie nie istnieje.', 'danger')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)