from flask import Blueprint, abort, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from sqlalchemy import asc
from .models import Event, Comment, User
from .forms import EventForm, CommentForm, BookingForm
from .utils import check_upload_file
from . import db

# Define Events Blueprint
events_bp = Blueprint('events', __name__, url_prefix='/events')

# Register Route: View Event
@events_bp.route('/<event_id>')
def show(event_id):
    event = db.session.scalar(db.select(Event).where(Event.id==event_id))
    if not event:
        abort(404) # Triggers @app.errorhandler
    comment_form = CommentForm()
    booking_form = BookingForm()
    return render_template('events/show.html', event=event, comment_form=comment_form, booking_form=booking_form)

# # Register Route: Book Event
# @events_bp.route('/<event_id>/book', methods=['GET', 'POST'])
# @login_required
# def book(event_id):
#     event = db.session.scalar(db.select(Event).where(Event.id==event_id))
#     if not event:
#         abort(404)
#     if event.status != 'Open':
#         flash('This event is not currently open for bookings.')
#         return redirect(url_for('events.show', event_id=event_id))
#     form = BookingForm()
#     if form.validate_on_submit():
#         print('Booking form submitted and validated')
#         # Check if there are enough tickets available
#         if event.available_tickets < form.tickets.data:
#             flash('Not enough tickets available for this booking.')
#             return redirect(url_for('events.show', event_id=event_id))

#         # Create a booking instance
#         booking = BookingForm(
#             user_id=current_user.id,
#             event_id=event.id,
#             tickets=form.tickets.data,
#             total_price=event.ticket_price * form.tickets.data
#         )
#         db.session.add(booking)
        
#         # Update the event's available tickets
#         event.available_tickets -= form.tickets.data
#         if event.available_tickets == 0:
#             event.status = 'Sold Out'
        
#         db.session.commit()
#         flash('Your booking was successful!')
#         print(f"Booking created: <user_id={current_user.id}, event_id={event.id}, tickets={form.tickets.data}>")
#         return redirect(url_for('events.show', event=event))

# Register Route: Post Comments on Event
@events_bp.route('/<event_id>/comment', methods=['GET', 'POST'])
@login_required
def comment(event_id):
    form = CommentForm()
    event = db.session.scalar(db.select(Event).where(Event.id==event_id))

    if form.validate_on_submit():
        comment = Comment(text=form.text.data, event=event, user=current_user)
        db.session.add(comment)
        db.session.commit()
        flash('Your comment was successfully posted.')
        print(f"Comment posted: <text='{comment.text}', username={comment.user.username}>")
        return redirect(url_for('events.show', event_id=event_id))
    return render_template('events/show.html', comment_form=form, id=event_id)

# Register Route: Create Event
@events_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = EventForm(create_event=True)

    # Pass checks & create event instance
    if form.validate_on_submit():
        db_file_path = check_upload_file(form)
        event = Event(
            title=form.title.data,
            artist=form.artist.data,
            genre=form.genre.data,
            venue=form.venue.data,
            location=form.location.data,
            date=form.date.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            available_tickets=form.available_tickets.data,
            ticket_price=form.ticket_price.data,
            short_description=form.short_description.data,
            description=form.description.data,
            image=db_file_path,
            status='Open',
            owner_id=current_user.id
        )
        
        db.session.add(event)
        db.session.commit()
        flash('Successfully created new event', 'success')
        return redirect(url_for('events.show', event_id=event.id))

    # Error Validation
    if form.errors:
        all_errors = ", ".join(
            err_msg
            for field_errors in form.errors.values()
            for err_msg in field_errors
        )
        flash(f"Cannot create event: {all_errors}")
    return render_template('events/create.html', form=form)

# Register Route: Manage All Events
@events_bp.route('/manage', methods=['GET', 'POST'])
@login_required
def owned_events():
    # Select events created by the user
    events = db.session.scalars(db.select(Event).where(Event.owner_id == current_user.id).order_by(Event.date, Event.start_time)).all()
    return render_template('events/owned.html', events=events)

# Register Route: Manage Specific Event
@events_bp.route('/manage/event-<id>', methods=['GET', 'POST'])
@login_required
def manage(id):
    user_id = current_user.id
    event = db.session.scalar(db.select(Event).where(Event.id == id))


    # If the event doesnt exist
    if not event:
        abort(404)
    # If the user does not own the event
    if event.owner_id != user_id:
        abort(403)

    
    form = EventForm(modify_event=True, obj=event)

    if form.validate_on_submit():
        db_file_path = check_upload_file(form)

        # If the number of available tickets was updated
        if form.available_tickets.data > event.available_tickets:
            if event.status == "Sold Out":
                event.status = "Open"

        # If the event is sold out - the number of tickets should not be reduced
        if event.status == "Sold Out":
            if form.available_tickets.data < event.available_tickets:
                flash("As the event is sold out, the number of tickets cannot be reduced.")
                return render_template('events/manage.html', event=event, form=form)

        # Setting modified fields
        event.title = form.title.data
        event.artist = form.artist.data
        event.genre = form.genre.data
        event.venue = form.venue.data
        event.location = form.location.data
        event.date = form.date.data
        event.start_time = form.start_time.data
        event.end_time = form.end_time.data
        event.available_tickets = form.available_tickets.data
        event.ticket_price = form.ticket_price.data
        event.short_description = form.short_description.data
        event.description = form.description.data

        print(form.available_tickets.data)

        # If the number of tickets is set to 0
        if form.available_tickets.data == 0:
            event.status = "Sold Out"

        # If the user did not provide a new event image
        if db_file_path != None:
            event.image = db_file_path

        # Commit the modifications
        db.session.commit()
        flash('Event updated successfully')
        return redirect(url_for('events.show', event_id=event.id))

    # If the form is not valid (extra validators)
    if form.errors:
        all_errors = ", ".join(
            err_msg
            for field_errors in form.errors.values()
            for err_msg in field_errors
        )
        flash(f"Cannot create event: {all_errors}")
    return render_template('events/manage.html', event=event, form=form)

# Register Route: Cancel Event
@events_bp.route('/manage/event-<id>/cancel')
@login_required
def cancel(id):
    user_id = current_user.id
    event = db.session.scalar(db.select(Event).where(Event.id == id))

    if not event:
        abort(404)
    if event.owner_id != user_id:
        abort(403)

    if event.status == 'Open' or event.status == 'Sold Out':
        event.status = 'Cancelled'
        db.session.commit()
        flash('Event cancelled successfully')
    else:
        flash('Unable to cancel event. Your event is either in the past or has previously been cancelled.')
    return redirect(url_for('events.owned_events'))