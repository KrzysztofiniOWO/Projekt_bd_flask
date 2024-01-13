from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import InputRequired, Length, EqualTo, ValidationError, Regexp
from helpers import is_username_available, is_email_available, is_phone_number_available

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[InputRequired(), Length(max=120)])
    phone_number = StringField('Phone Number', validators=[InputRequired(), Length(min=1, max=20)])
    
    password_policy_message = "Password must be at least 8 characters long, and contain at least one lowercase letter, one uppercase letter, one digit, and one special character"

    password = PasswordField('Password', validators=[
        InputRequired(),
        Length(min=8, max=60, message="Password must be at least 8 characters long"),
        Regexp(
            regex="^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%^&*()_+{}|:<>?~])",
            message=password_policy_message
        )
    ])

    confirm_password = PasswordField('Confirm Password', validators=[
        InputRequired(),
        EqualTo('password', message='Passwords must match')
    ])

    authentication_type = SelectField('Second Authentication Type', choices=[
        ('second_email', 'Support email'),
        ('phone', 'SMS code'),
        ('authy_app', 'Authy application')],
        validators=[InputRequired()]
    )
    
    terms_of_service_consent = BooleanField('I accept the Terms of Service.')
    newsletter_consent = BooleanField('I want to receive the Newsletter.')
    location_processing_consent = BooleanField('I consent to the processing of my location data to find the nearest kebab places.')
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        if not is_username_available(username.data):
            raise ValidationError('This username is already taken. Please choose another one.')

    def validate_email(self, email):
        if not is_email_available(email.data):
            raise ValidationError('This email is already registered. Please use a different email.')

    def validate_phone_number(self, phone_number):
        if not is_phone_number_available(phone_number.data):
            raise ValidationError('This phone number is already registered. Please use a different phone number.')
        
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6, max=60)])
    submit = SubmitField('Log In')
