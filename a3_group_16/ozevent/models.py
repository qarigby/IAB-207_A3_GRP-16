from . import db
from sqlalchemy.sql import func
from sqlalchemy import Numeric
from flask_login import UserMixin

# Users Table
class User(db.Model, UserMixin):
    __tablename__ = 'users'

    # Table Columns (Attributes)
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(100), index=True, unique=True, nullable=False)
    email = db.Column(db.String(100), index=True, unique=True, nullable=False)
    profile_pic = db.Column(db.String(400), nullable=False, default='default_profile.png')
    phone_number = db.Column(db.String(10), nullable=False)
    street_address = db.Column(db.String(255), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    # Relation to Comments:
    comments = db.relationship('Comment', backref='user')
    # Relation to Bookings:
    bookings = db.relationship('Booking', backref='user')
    # Relation to Events:
    events = db.relationship('Event', backref='user')

    # String Representation (Database)
    def __repr__(self):
        return f"<User id={self.id}, username='{self.username}'>"

# Events Table
class Event(db.Model):
    __tablename__ = 'events'

    # Table Columns (Attributes)
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), index=True, nullable=False)
    artist = db.Column(db.String(100), index=True) # Artist announcements may be delayed
    genre = db.Column(db.String(50), index=True, nullable=False)
    venue = db.Column(db.String(150), index=True, nullable=False)
    location = db.Column(db.String(150), index=True, nullable=False)
    date = db.Column(db.Date, index=True, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    short_description = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(400), nullable=False, default='/static/img/default_event.png')
    status = db.Column(db.String(50), index=True, nullable=False)

    # Table Relations
    comments = db.relationship('Comment', backref='event')
    bookings = db.relationship('Booking', backref='event')
    tickets = db.relationship('Ticket', backref='event')

    # Foreign Key
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # String Representation (Database)
    def __repr__(self):
        return f"<Event id={self.id}, title='{self.title}', venue='{self.venue}', date={self.date}>"

# Comments Table
class Comment(db.Model):
    __tablename__ = 'comments'

    # Table Columns (Attributes)
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(400), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())

    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)

    # String Representation (Database)
    def __repr__(self):
        preview = (self.text[:20] + '...') if len(self.text) > 20 else self.text
        return f"<Comment id={self.id}, text='{preview}', user_id={self.user_id}, event_id={self.event_id}>"

# Bookings Table
class Booking(db.Model):
    __tablename__ = 'bookings'

    # Table Columns (Attributes)
    id = db.Column(db.Integer, primary_key=True)
    ref_code = db.Column(db.String(10), index=True, unique=True, nullable=False)
    num_tickets = db.Column(db.Integer, nullable=False)
    date_booked = db.Column(db.DateTime, nullable=False, server_default=func.now())

    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'), nullable=False)

    # Table Relations
    ticket = db.relationship('Ticket', backref='bookings')

    # String Representation (Database)
    def __repr__(self):
        return f"<Booking id={self.id}, reference='{self.ref_code}', user_id={self.user_id}, event_id={self.event_id}, ticket_id={self.ticket_id}, num_tickets={self.num_tickets}>>"
    
# Tickets Table
class Ticket(db.Model):
    __tablename__ = 'ticket'

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    ticket_type = db.Column(db.String(50), nullable=False)
    available_tickets = db.Column(db.Integer, nullable=False)
    ticket_price = db.Column(Numeric(7, 2), nullable=False)

    # Foreign Keys
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)

    # String Representation (Database)
    def __repr__(self):
        return f"<Ticket id={self.id}, ticket_type='{self.ticket_type}', available_tickets={self.available_tickets}, ticket_price={self.ticket_price}>"
