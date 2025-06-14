from flask import Blueprint, flash, render_template, request, redirect, url_for
from flask_login import current_user, login_required
from .models import Booking
from . import db 

booking_bp = Blueprint('booking', __name__)

# need to implement this still
@booking_bp.route('/bookings')
@login_required
def bookings():
    bookings = db.session.scalars(db.select(Booking).where(Booking.user_id == current_user.id)).all()
    return render_template('booking_history.html', bookings=bookings)
    
    