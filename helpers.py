import mysql.connector
from flask import current_app
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

def get_db_connection():
    with current_app.app_context():
        return mysql.connector.connect(
            host=current_app.config['MYSQL_DATABASE_HOST'],
            user=current_app.config['MYSQL_DATABASE_USER'],
            password=current_app.config['MYSQL_DATABASE_PASSWORD'],
            database=current_app.config['MYSQL_DATABASE_DB'],
            port=current_app.config['MYSQL_DATABASE_PORT'],
        )

def execute_sql_query(sql, values=None, fetchone=False, commit=False):
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        if values:
            cursor.execute(sql, values)
        else:
            cursor.execute(sql)

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
    except Exception as e:
        print(f"Error executing SQL query: {e}")
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
    sql_insert_email_verification = (
        "INSERT INTO email_verification (email, verification_code, code_expiry_time, verification_link, link_expiry_time, created_at)"
        "VALUES (%s, 'dummy_code', NOW(), 'dummy_link', NOW(), NOW())"
    )
    values_insert_email_verification = (
        email,
    )

    sql_insert_user = (
        "INSERT INTO users"
        "(username, email, phone_number, password, authentication_type, terms_of_service_consent, newsletter_consent, location_processing_consent, created_at)"
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())"
    )
    values_insert_user = (
        username, email, phone_number, password,
        authentication_type, terms_of_service_consent,
        newsletter_consent, location_processing_consent
    )

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        # Wstawienie do tabeli email_verification
        cursor.execute(sql_insert_email_verification, values_insert_email_verification)
        connection.commit()
        print("Email verification inserted successfully")

        # Wstawienie do tabeli users
        cursor.execute(sql_insert_user, values_insert_user)
        connection.commit()
        print("User inserted successfully")

    except Exception as e:
        print(f"Error inserting user: {e}")
    finally:
        cursor.close()
        connection.close()

def is_username_available(username):
    sql = "SELECT 1 FROM users WHERE username = %s"
    values = (username,)
    result = execute_sql_query(sql, values, fetchone=True)
    return result is None

def is_email_available(email):
    sql = "SELECT 1 FROM users WHERE email = %s"
    values = (email,)
    result = execute_sql_query(sql, values, fetchone=True)
    return result is None

def is_phone_number_available(phone_number):
    sql = "SELECT 1 FROM users WHERE phone_number = %s"
    values = (phone_number,)
    result = execute_sql_query(sql, values, fetchone=True)
    return result is None