from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import InputRequired, Length, Email, EqualTo

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
