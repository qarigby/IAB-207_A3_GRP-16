from . import db
from sqlalchemy.sql import func
from flask_login import UserMixin

# Users Table
class User(db.Model, UserMixin):
    __tablename__ = 'users'

    # Table Columns (Attributes)
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), index=True, unique=True, nullable=False)
    email = db.Column(db.String(100), index=True, unique=True, nullable=False)
    phone_num = db.Column(db.String(20), index=True, unique=True, nullable=False)
    street_address = db.Column(db.String(255), nullable=False) # Addresses aren't unique
    password_hash = db.Column(db.String(255), nullable=False)
    user_type = db.Column(db.String(20), nullable=False, default='explorer') # /organiser

    # Table Relations
    # user.comments OR comment.posted_by
    comments = db.relationship('Comment', backref='posted_by')
    # user.bookings OR booking.placed_by
    bookings = db.relationship('Booking', backref='placed_by')
    # user.events OR event.created_by
    events = db.relationship('Event', backref='created_by')

    # String Representation (Database)
    def __repr__(self):
        return f"<User id={self.id}, username='{self.username}', user_type='{self.user_type}'>"

# Events Table
class Event(db.Model):
    __tablename__ = 'events'

    # Table Columns (Attributes)
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), index=True, nullable=False)
    artist = db.Column(db.String(100), index=True) # Artist announcements may be delayed
    genre = db.Column(db.String(50), index=True, nullable=False)
    venue = db.Column(db.String(150), index=True, nullable=False)
    date = db.Column(db.Date, index=True, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
    available_tickets = db.Column(db.Integer, nullable=False)
    summary = db.Column(db.String(250), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    image = db.Column(db.String(400), nullable=False, default='/static/img/default.png')
    status = db.Column(db.String(50), index=True, nullable=False)

    # Table Relations
    # event.comments OR comment.event
    comments = db.relationship('Comment', backref='event')
    # event.bookings OR booking.event
    bookings = db.relationship('Booking', backref='event')

    # Foreign Key
    organiser_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # String Representation (Database)
    def __repr__(self):
        return f"<Event id={self.id}, title='{self.title}', venue='{self.venue}', date={self.date}>"

# Comments Table
class Comment(db.Model):
    __tablename__ = 'comments'

    # Table Columns (Attributes)
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(400), nullable=False)
    posted_at = db.Column(db.DateTime, nullable=False, server_default=func.now())

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
    ref_code = db.Column(db.String(50), index=True, unique=True, nullable=False)
    num_tickets = db.Column(db.Integer, nullable=False)
    placed_at = db.Column(db.DateTime, nullable=False, server_default=func.now())

    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)

    # String Representation (Database)
    def __repr__(self):
        return f"<Booking id={self.id}, reference='{self.ref_code}', user_id={self.user_id}, event_id={self.event_id}>"