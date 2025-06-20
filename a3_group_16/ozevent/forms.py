from flask_wtf import FlaskForm, Form
from wtforms import FieldList, FormField
from wtforms.fields import TextAreaField, SubmitField, StringField, PasswordField, DateField, TimeField, IntegerField, SelectField, DecimalField
from wtforms.validators import InputRequired, DataRequired, Length, Email, EqualTo, ValidationError, NumberRange, Regexp
from flask_wtf.file import FileRequired, FileField, FileAllowed
import re
from datetime import date, datetime
from . import db
from .models import Event

# Image Uploads (User Profile/Events)
file_format = ['png', 'jpg', 'jpeg', 'webp'] # File types allowed

# Login Form
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired('Please enter your username.')])
    password = PasswordField('Password', validators=[InputRequired('Please enter your password.')])
    submit = SubmitField('Log In')

# Registration Form
class RegisterForm(FlaskForm):
    firstname = StringField('First Name', validators=[InputRequired('Please enter your first name.'), Length(max=50, message='Input exceeds maximum length.')])
    surname = StringField('Surname', validators=[InputRequired('Please enter your surname.'), Length(max=50, message='Input exceeds maximum length.')])
    username = StringField('Username', validators=[InputRequired('Please enter a username.'), Length(max=100, message='Input exceeds maximum length.')])
    email = StringField('Email Address', validators=[Email('Please enter a valid email.'), Length(max=100, message='Input exceeds maximum length.')])
    phone_number = StringField('Phone Number', validators=[InputRequired('Please enter a phone number.'), 
                                                           Length(min=10, max=10, message='Phone number must be 10 digits.'), 
                                                           Regexp(r'^\d+$', message='Phone number must contain digits only.')])
    image = FileField('Profile Picture', validators=[FileAllowed(file_format, 'Only JPG, WEBP or PNG file formats are accepted.')]) # Images are optional
    street_address = TextAreaField('Street Address', validators=[InputRequired('Please enter a street address.'), Length(max=255, message='Input exceeds maximum length.')])
    password = PasswordField('Password', validators=[InputRequired('Please enter a password.'), Length(min=8, message='Password must be at least 8 characters long.')])
    confirm = PasswordField('Confirm Password', validators=[EqualTo('password', message='Passwords must match.')]) # Password Confirmation
    submit = SubmitField('Register')

    # More password validation (automatically called by WTForms)
    def validate_password(self, field):
        password = field.data

        # Password must include at least one symbol
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            raise ValidationError('Password must include at least one symbol (!@#$%^&*).')

        # Password must include at least one number
        if not re.search(r"\d", password):
            raise ValidationError('Password must include at least one number.')

# Genre Choices (Event Creation)
genre_choices = [
    ('', 'Select a genre'),  # Placeholder
    ('alternative', 'Alternative'),
    ('blues', 'Blues'),
    ('classical', 'Classical'),
    ('country', 'Country'),
    ('drum & bass', 'Drum & Bass'),
    ('edm', 'EDM'),
    ('folk', 'Folk'),
    ('hip-hop', 'Hip-Hop'),
    ('jazz', 'Jazz'),
    ('latin', 'Latin'),
    ('metal', 'Metal'),
    ('opera', 'Opera'),
    ('pop', 'Pop'),
    ('reggae', 'Reggae'),
    ('r&b', 'R&B'),
    ('rock', 'Rock'),
    ('soul', 'Soul'),
    ('other', 'Other')
    ]

# Ticket Form
class TicketForm(Form):
    ticket_type = StringField('Ticket Type', validators=[InputRequired('Ticket Type must be provided'), Length(max=50, message='Input exceeds maximum length')])
    available_tickets = IntegerField('Available Tickets', validators=[InputRequired("Please enter the number of tickets available")])
    ticket_price = DecimalField('Price ($)', validators=[InputRequired("Please enter ticket price"), NumberRange(min=0)])       

# Event Creation Form
class EventForm(FlaskForm):
    title = StringField('Event Title', validators=[InputRequired('Please enter the event title.'), Length(max=100, message='Input exceeds maximum length.')])
    artist = TextAreaField('Artist(s)', validators=[Length(max=100, message='Input exceeds maximum length.')]) # Artists are optional
    genre = SelectField('Genre', choices=genre_choices, validators=[InputRequired(message='Please select a genre.'), Length(max=50, message='Input exceeds maximum length.')])
    custom_genre = StringField('Other Genre', validators=[Length(max=50, message='Input exceeds maximum length.')]) # For users who select 'Other' as genre
    venue = StringField('Venue', validators=[InputRequired('Please enter the venue.'), Length(max=150, message='Input exceeds maximum length.')])
    location = StringField('Location', validators=[InputRequired('Please enter the location.'), Length(max=150, message='Input exceeds maximum length.')])
    date = DateField('Date', format='%Y-%m-%d', validators=[InputRequired('Please enter a date.')])
    start_time = TimeField('Start Time', format='%H:%M', validators=[InputRequired('Please enter a start time.')])
    end_time = TimeField('End Time', format='%H:%M', validators=[InputRequired('Please enter an end time.')])
    tickets = FieldList(FormField(TicketForm), min_entries=1)
    short_description = TextAreaField('Short Description', validators=[InputRequired('Please enter a brief event description.'),
                                                                       Length(max=255, message='Cannot exceed 255 characters.')])
    description = TextAreaField('Description', validators=[InputRequired('Please enter a regular event description.'), Length(max=1000, message='Cannot exceed 1000 characters.')])

    description = TextAreaField('Description', validators=[InputRequired('Please enter a regular event description')])
    image = FileField('Cover Image', validators=[FileAllowed(file_format, 'Only JPG, WEBP or PNG file formats are accepted.')]) # Images are optional
    submit = SubmitField('Create Event')

    def __init__(self, create_event=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._create_event = create_event

        # available_tickets cannot be set to 0 during event creation
        if self._create_event:
            for ticket_form in self.tickets:
                ticket_form.form.available_tickets.validators = [InputRequired('Please enter the number of tickets available.'), NumberRange(min=1, message='Available ticket quantity must be greater than 1.')]
    
    # Field Validators
    def validate_custom_genre(self, field):
        if self.genre.data == 'Other' and not field.data.strip():
            raise ValidationError('Please enter the genre.')

    def validate_date(self, field):
        if field.data and field.data < date.today():
            raise ValidationError('Date cannot be in the past.')
        
    def validate(self, extra_validators=None):
        # Run default validations first
        if not super().validate():
            return False

        # Cross-field Validation
        start = self.start_time.data
        end = self.end_time.data

        # Ensures start & end-time validation
        if start == end:
            self.end_time.errors.append('End time cannot be the same as start time.')
            return False
        elif start > end:
            self.end_time.errors.append('End time must be after start time.')
            return False
        
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
                self.title.errors.append('An event with this title, artist(s), date and start time already exists.')
                return False
        return True

# Event Booking Form
class BookingForm(FlaskForm):
    ticket_type = SelectField('Ticket Type',  coerce=int, validators=[InputRequired('Please select a ticket.')])
    num_tickets = IntegerField('Ticket(s)', validators=[InputRequired('Please enter the number of tickets you wish to book.'), NumberRange(min=1, message='Must be at least 1.')])
    submit = SubmitField('Book Now')

# Event Comment Form
class CommentForm(FlaskForm):
    text = TextAreaField('Post a comment', [DataRequired('Please enter your comment.'), Length(min=1, max=400, message='Input must be between 1 and 400 characters.')])
    submit = SubmitField('Post')