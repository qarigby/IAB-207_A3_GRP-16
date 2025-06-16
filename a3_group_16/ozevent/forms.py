from flask_wtf import FlaskForm
from wtforms.fields import TextAreaField, SubmitField, StringField, PasswordField, DateField, TimeField, IntegerField, SelectField, DecimalField
from wtforms.validators import InputRequired, Length, Email, EqualTo, ValidationError, NumberRange, Regexp
from flask_wtf.file import FileRequired, FileField, FileAllowed
import re
from datetime import date, datetime
from . import db
from .models import Event

file_format = ['png', 'jpg', 'jpeg', 'webp'] # File types allowed for image upload

# Login Form
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired('Please enter your username')])
    password = PasswordField('Password', validators=[InputRequired('Please enter your password')])
    submit = SubmitField('Log In')

# Registration Form
class RegisterForm(FlaskForm):
    firstname = StringField('First Name', validators=[InputRequired('Please enter your first name'), Length(max=50, message='Input too long')])
    surname = StringField('Surname', validators=[InputRequired('Please enter your surname'), Length(max=50, message='Input too long')])
    username = StringField('Username', validators=[InputRequired('Please enter a username'), Length(max=100, message='Input too long')])
    email = StringField('Email Address', validators=[Email('Please enter a valid email'), Length(max=100, message='Input too long')])
    phone_number = StringField('Phone Number', validators=[InputRequired('Please enter a phone number'), 
                                                           Length(min=10, max=10, message='Phone number must be 10 digits'), 
                                                           Regexp(r'^\d+$', message='Phone number must contain digits only')])
    image = FileField('Profile Picture', validators=[FileAllowed(file_format, 'Only JPG, WEBP or PNG file formats are accepted.')]) # Images are optional
    street_address = TextAreaField('Street Address', validators=[InputRequired('Please enter a street address'), Length(max=255, message='Input too long')])
    password = PasswordField('Password', validators=[InputRequired('Please enter a password.'), Length(min=8, message='Password must be at least 8 characters long')])
    confirm = PasswordField('Confirm Password', validators=[EqualTo('password', message='Passwords must match.')]) # Password Confirmation
    submit = SubmitField('Register')

    # More password validation (automatically called by WTForms)
    def validate_password(self, field):
        password = field.data

        # Password must include at least one symbol
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            raise ValidationError("Password must include at least one symbol (!@#$%^&* etc)")

        # Password must include at least one number
        if not re.search(r"\d", password):
            raise ValidationError("Password must include at least one number")

# Comment Posting Form
class CommentForm(FlaskForm):
    text = TextAreaField('Post a comment', [InputRequired('Please enter your comment'), Length(max=400, message="Input too long")])
    submit = SubmitField('Post')

# Event Creation Form
genre_choices = [
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
    title = StringField('Event Title', validators=[InputRequired('Please enter the event title'), Length(max=100, message='Input too long')])
    artist = StringField('Artist Name(s)', validators=[Length(max=100, message='Input too long')]) # Artists are optional
    genre = SelectField('Genre', choices=genre_choices, validators=[InputRequired(message='Please select a genre'), Length(max=50, message='Input too long')])
    venue = StringField('Venue', validators=[InputRequired('Please enter the venue'), Length(max=150, message='Input too long')])
    location = StringField('Location', validators=[InputRequired('Please enter the location'), Length(max=150, message='Input too long')])
    date = DateField('Date', format='%Y-%m-%d', validators=[InputRequired('Please enter a date')])
    start_time = TimeField('Start Time', format='%H:%M', validators=[InputRequired('Please enter a start time')])
    end_time = TimeField('End Time', format='%H:%M', validators=[InputRequired('Please enter an end time')])
    available_tickets = IntegerField('Available Tickets', validators=[InputRequired('Please enter the number of tickets available'), 
                                                                      NumberRange(min=1, message='Quantity must be greater than 1')])
    ticket_price = StringField('Ticket Price', validators=[InputRequired('Please enter the ticket price'), 
                                                               Length(max=7, message='Cannot be more than $99,999.99'), Regexp(r'^\d{1,5}(\.\d{1,2})?$')])
    short_description = TextAreaField('Short Description', validators=[InputRequired('Please enter a brief event description'),
                                                                       Length(max=255, message='Must be less than 255 characters long')])
    description = TextAreaField('Description', validators=[InputRequired('Please enter a regular event description')])
    image = FileField('Cover Image', validators=[FileAllowed(file_format, 'Only JPG, WEBP or PNG file formats are accepted.')]) # Images are optional
    submit = SubmitField('Create')

    def __init__(self, create_event=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._create_event = create_event
    
    # Field Validators
    def validate_date(self, field):
        if field.data and field.data < date.today():
            raise ValidationError('Date cannot be in the past')
        
    def validate(self, extra_validators=None):
        # Run default validations first
        if not super().validate():
            return False

        # Cross-field Validation
        start = self.start_time.data
        end = self.end_time.data

        # Ensures start & end-time validation
        if start == end:
            self.end_time.errors.append('End time cannot be the same as start time')
            return False
        elif start > end:
            self.end_time.errors.append('End time must be after start time')
            return False
        
        # Altering validators for modifying events
        if self._create_event: 
            # Ensuring event is not a duplicate
            existing = db.session.scalar(
                db.select(Event).where(
                    Event.title == self.title.data,
                    Event.artist == self.artist.data,
                    Event.date == self.date.data,
                    Event.start_time == self.start_time.data,
                )
            )
            if existing:
                self.title.errors.append('An event with this title, artist(s), date, and start time already exists')
                return False
            
            # Removing minimum number validator so owner can remove all available tickets (triggering the event to sell out)
            self.available_tickets.validators = [
                validator for validator in self.available_tickets.validators
                if not isinstance(validator, NumberRange)
            ]
        return True