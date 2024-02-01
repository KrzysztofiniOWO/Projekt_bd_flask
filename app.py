from flask import Flask, render_template, redirect, url_for, flash, session, request
from forms import RegistrationForm, LoginForm
from helpers import execute_sql_query, insert_user, insert_email_verification
from helpers import is_username_available, is_email_available, is_phone_number_available, get_user_data_by_username
from flask_bcrypt import Bcrypt
from flask import jsonify

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

    #sql = "SELECT local_name, description, rating FROM local_accounts WHERE district_id IN (SELECT district_id FROM districts WHERE district = %s)"
    sql = "SELECT local_name, description, rating FROM local_accounts INNER JOIN districts ON local_accounts.district_id = districts.district_id WHERE districts.district = %s"
    values = (district_name,)
    local_accounts = execute_sql_query(sql, values, fetchone=False)

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
    

def insert_opinion_into_database(insert_dict):
    # Pobierz id lokalu na podstawie lokal_name
    sql = "SELECT id FROM local_accounts WHERE local_name = %s"
    values = (insert_dict['lokal_name'],)
    lokal_id = execute_sql_query(sql, values, fetchone=True)


    insert_query = str(f"""INSERT INTO reviews (local_id, username, title, content, rating, likes_counter, dislikes_counter, review_status, is_image_verified, created_at) 
    VALUES ({int(lokal_id[0])}, '{insert_dict['username']}', '{insert_dict['title']}', '{insert_dict['content']}',  {int(insert_dict['rating'])}, 0, 0, 0, 0, NOW() )""")
    print(insert_query, end='\n\n')
    
    # values = (insert_dict.username, insert_dict.title, insert_dict.content, insert_dict.rating)
    execute_sql_query(insert_query, commit=True)
    print('Opinion inserted into database')

    
@app.route('/reviews', methods=['GET', 'POST'])
def reviews():


    try:
        lokal_name = request.args.get('lokal_name')
    except Exception as e:
        print(e)
        return render_template('oceny.html', message='Error')

    sql = "SELECT reviews.username, reviews.content, reviews.rating, reviews.likes_counter, reviews.dislikes_counter FROM reviews INNER JOIN local_accounts ON reviews.local_id = local_accounts.id WHERE local_accounts.local_name = %s"
    #sql = "SELECT * FROM local_accounts WHERE local_name = %s"
    values = (lokal_name,)
    reviews_result = execute_sql_query(sql, values=values, fetchone=False)

    if session.get('info'):
        return render_template('oceny.html', reviews=reviews_result, lokal_name=lokal_name, accept_review=False)

    return render_template('oceny.html', reviews=reviews_result, lokal_name=lokal_name)

@app.route('/add_review', methods=['POST'])
def add_review():
    try:
        lokal_name = request.args.get('lokal_name')
    except Exception as e:
        print(e)
        return render_template('oceny.html', message='Error')

    username = session.get('username')
    title = request.form.get('title')
    content = request.form.get('content')
    rating = request.form.get('rating')

    insert_dict = {
        'lokal_name': lokal_name,
        'username': username,
        'title': title,
        'content': content,
        'rating': rating
    }

    insert_opinion_into_database(insert_dict)

    if session.get('info'):
        return redirect(url_for('reviews', lokal_name=lokal_name))

    return redirect(url_for('reviews', lokal_name=lokal_name))



if __name__ == '__main__':
    app.run(debug=True)