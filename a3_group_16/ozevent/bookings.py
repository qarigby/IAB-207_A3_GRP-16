from flask import Blueprint, abort, flash, render_template, request, redirect, url_for
from flask_login import current_user, login_required
from .models import Booking, Event, Ticket
from . import db 
from sqlalchemy.orm import joinedload

booking_bp = Blueprint('booking', __name__)

# need to implement this still
@booking_bp.route('/bookings')
@login_required
def bookings():
    # Checks if the user has a booking
    booking_exist = db.session.scalar(db.select(Booking).where(Booking.user_id == current_user.id))

    # Get the requested status
    status = request.args.get("status", "all").capitalize()

    # Format sold-out status correctly
    if status == "Sold out":
        status = "Sold Out"

    # No filtering applied
    if status == "All":
        bookings = db.session.scalars(
            db.select(Booking)
            .join(Booking.event)
            .options(joinedload(Booking.event))  # load event data to avoid N+1 issues
            .where(Booking.user_id == current_user.id)
            .order_by(Event.date, Event.start_time) 
        ).all()
    # Filtering applied
    else:
        bookings = db.session.scalars(
            db.select(Booking)
            .join(Booking.event)
            .options(joinedload(Booking.event))
            .where(Booking.user_id == current_user.id, Event.status == status)
            .order_by(Event.date, Event.start_time) 
        ).all()
    return render_template('booking_history.html', bookings=bookings, active_status=status, booking_exist=booking_exist)

# Cancelling a booking
@booking_bp.route('/bookings/cancel/<booking_id>')
@login_required
def cancel(booking_id):
    booking = db.session.scalar(db.select(Booking).where(Booking.id == booking_id))
    event = db.session.scalar(db.select(Event).where(Event.id == booking.event.id))
    ticket = db.session.scalar(db.select(Ticket).where(Ticket.id == booking.ticket.id))

    # if the booking doesnt exist
    if not booking:
        abort(404)
    # If the user does not own the booking
    if booking.user_id != current_user.id:
        abort(403)

    # Add the number of tickets being cancelled back to the event
    ticket.available_tickets = ticket.available_tickets + booking.num_tickets

    # If the event was sold out - it now isnt 
    if event.status == "Sold Out":
        event.status = "Open"
    
    # if the event is open (can't cancel bookings for inactive or cancelled events)
    if event.status == 'Open' or event.staus == "Sold Out":
        db.session.delete(booking) #delete the booking from db
        db.session.commit()
        flash('Booking cancelled successfully.')
    else:
        flash('Unable to cancel booking. The event is either in the past or has previously been cancelled.')
    return redirect(url_for('booking.bookings', event_id=event.id))

    
    # Still need to add filtering so users can view open, inactive, and cancelled events by status