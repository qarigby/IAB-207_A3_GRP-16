from . import db
from datetime import datetime
from flask_login import UserMixin

# Users table
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), index=True, unique=True, nullable=False)
    email = db.Column(db.String(100), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    # Relation to Comments:
    comments = db.relationship('Comment', backref='user')
    # Relation to Bookings:
    bookings = db.relationship('Booking', backref='user')
    # Relation to Events:
    eents = db.relationship('Event', backref='user')

# Events table
class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    artist = db.Column(db.String(100))
    genre = db.Column(db.String(50), index=True, nullable=False)
    venue = db.Column(db.String(150), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    available_tickets = db.Column(db.Integer, nullable=False)
    short_description = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(400), nullable=False)
    status = db.Column(db.String(50), nullable=False)

    # Relation to Comments:
    comments = db.relationship('Comment', backref='event')
    # Relation to Bookings:
    bookings = db.relationship('Booking', backref='event')

    # Adding the foreign key
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))

# Comments table
class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(400))
    created_at = db.Column(db.DateTime, default=datetime.now())

    # Adding the foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))

# Bookings table
class Booking(db.Model):
    __tablename__ = "bookings"
    id = db.Column(db.Integer, primary_key=True)
    order_reference = db.Column(db.String(10), index=True, nullable=False)
    num_tickets = db.Column(db.Integer, nullable=False)

    # Adding the foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))