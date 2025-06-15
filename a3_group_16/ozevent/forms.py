from flask_wtf import FlaskForm
from wtforms import SelectField
from wtforms.fields import TextAreaField, SubmitField, StringField, PasswordField, DateField, TimeField, IntegerField
from wtforms.validators import InputRequired, Length, Email, EqualTo, ValidationError, NumberRange, Regexp
from flask_wtf.file import FileRequired, FileField, FileAllowed
import re
from datetime import date


'''Need to check that the validators for the register form and event form work properly (some are custom)'''

# File types allowed for image upload
ALLOWED_FILES = {'PNG','JPG','png','jpg'}

# Login Form
class LoginForm(FlaskForm):
    username=StringField("Username", validators=[InputRequired('Please enter your username')])
    password=PasswordField("Password", validators=[InputRequired('Please enter your password')])
    submit = SubmitField("Login")

# Registration Form
class RegisterForm(FlaskForm):
    firstname = StringField("First Name", validators=[InputRequired('Please enter your first name'), Length(max=50, message="Input too long")])
    surname=StringField("Surname", validators=[InputRequired('Please enter your surname'), Length(max=50, message="Input too long")])
    username = StringField("Username", validators=[InputRequired('Please enter a username'), Length(max=100, message="Input too long")])
    email = StringField("Email Address", validators=[Email("Please enter a valid email"), Length(max=100, message="Input too long")])
    phone_number = StringField("Phone Number", validators=[InputRequired("Please enter a phone number"), Length(min=10, max=10, message="Phone number must be 10 digits"), Regexp(r'^\d+$', message="Phone number must contain digits only")])
    address = TextAreaField("Address", validators=[InputRequired("Please enter an address"), Length(max=255, message="Input too long")])

    # linking two fields - password should be equal to data entered in confirm
    password=PasswordField("Password", validators=[InputRequired('Please enter a password'), Length(min=8, message="Password must be at least 8 characters long"),
                  EqualTo('confirm', message="Passwords must match")])
    confirm=PasswordField("Confirm Password")

    # submit button
    submit = SubmitField("Register")

    # More password validation (automatically called by WTForms)
    def validate_password(self, field):
        password = field.data

        # password must include at least one symbol
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            raise ValidationError("Password must include at least one symbol (!@#$%^&* etc)")

        # password must include at least one number
        if not re.search(r"\d", password):
            raise ValidationError("Password must include at least one number")

# Comment Posting Form
class CommentForm(FlaskForm):
    text = TextAreaField('Comment', [InputRequired('Please enter your comment'), Length(max=400, message="Input too long")])
    submit = SubmitField('Post')


# Event Creation Form
GENRE_CHOICES = [
    ('', 'Select a genre'),  # Placeholder
    ('rock', 'Rock'),
    ('hip-hop', 'Hip-Hop'),
    ('pop', 'Pop'),
    ('edm', 'EDM'),
    ('r&b', 'R & B'),
    ('latin', 'Latin'),
    ('k-pop', 'K-Pop'),
    ('country', 'Country'),
    ('jazz', 'Jazz'),
    ('classical', 'Classical')
]

class EventForm(FlaskForm):
    name = StringField("Event Name", validators=[InputRequired('Please enter the event name'), Length(max=100, message="Input too long")])
    artist = StringField("Artist Name(s)", validators=[InputRequired('Please enter the artist name(s)'), Length(max=100, message="Input too long")])
    genre = SelectField('Genre', choices=GENRE_CHOICES, validators=[InputRequired(message='Please select a genre'), Length(max=50, message="Input too long")])
    venue = StringField('Venue', validators=[InputRequired('Please enter a venue'), Length(max=150, message="Input too long")])
    date = DateField('Date', format='%Y-%m-%d', validators=[InputRequired('Please enter a date')])
    start_time = TimeField('Start Time', format='%H:%M', validators=[InputRequired('Please enter a start time')])
    end_time = TimeField('End Time', format='%H:%M', validators=[InputRequired('Please enter an end time')])
    available_tickets = IntegerField('Number of Available Tickets', validators=[InputRequired('Please enter the number of available tickets'), NumberRange(min=1, message="Quantity must be greater than 1")])
    ticket_price = StringField('Ticket Price ($)', validators=[InputRequired("Please enter the ticket price"), Length(max=5, message="Cannot be more than $99,999"), Regexp(r'^\d+(\.\d{1,2})?$', message="Must only contain digits or decimal point")])
    short_description = TextAreaField('Short Description', validators=[InputRequired('Please enter a short description'), Length(max=255, message="Must be less than 255 characters long")])
    description = TextAreaField('Description', validators=[InputRequired('Please enter a description of the event')])
    image = FileField('Cover Image', validators=[FileRequired(message='An image must be uploaded'), FileAllowed(ALLOWED_FILES, message='Only PNG or JPG files allowed')])
    submit = SubmitField('Create')
    
    # Field validators

    def validate_date(self, field):
        if field.data < date.today():
            raise ValidationError("Date cannot be in the past")
        
    def validate(self, extra_validators=None):
        # Run default validations first
        if not super().validate():
            return False

        # Cross-field validation
        start = self.start_time.data
        end = self.end_time.data

        # Ensures start and end-time validation
        if start == end:
            self.end_time.errors.append("End time cannot be the same as start time.")
            return False
        elif start > end:
            self.end_time.errors.append("End time must be after start time.")
            return False

        return True


# tell users the password validation requriements in the registration form.