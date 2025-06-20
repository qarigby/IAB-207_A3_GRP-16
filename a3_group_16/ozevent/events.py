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
    event = db.session.get(Event, event_id)
    if not event:
        abort(404) # Triggers @app.errorhandler
    comment_form = CommentForm()
    booking_form = BookingForm()
    return render_template('events/show.html', event=event, comment_form=comment_form, booking_form=booking_form)

# # Register Route: Book Event
# @events_bp.route('/<event_id>/book', methods=['GET', 'POST'])
# @login_required
# def book(event_id):
#     event = db.session.get(Event, event_id)
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
    comment_form = CommentForm()
    event = db.session.get(Event, event_id)
    if not event:
        abort(404) # Triggers @app.errorhandler
    if comment_form.validate_on_submit():
        comment = Comment(text=comment_form.text.data, event=event, user=current_user)
        db.session.add(comment)
        db.session.commit()
        flash('Your comment was successfully posted.')
        print(f"Comment posted: <text='{comment.text}', username={comment.user.username}>")
        return redirect(url_for('events.show', event_id=event_id))
    # If method is GET or form is invalid
    return render_template('events/show.html', comment_form=comment_form, event=event)

# Register Route: Create Event
@events_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    event_form = EventForm(create_event=True)

    # Pass checks & create event instance
    if event_form.validate_on_submit():
        db_file_path = check_upload_file(event_form)

        # If the user specifies a custom genre
        if event_form.genre.data == "other":
            genre = event_form.custom_genre.data
        else:
            genre = event_form.genre.data

        new_event = Event(
            title=event_form.title.data,
            artist=event_form.artist.data,
            genre=genre,
            venue=event_form.venue.data,
            location=event_form.location.data,
            date=event_form.date.data,
            start_time=event_form.start_time.data,
            end_time=event_form.end_time.data,
            available_tickets=event_form.available_tickets.data,
            ticket_price=event_form.ticket_price.data,
            short_description=event_form.short_description.data,
            description=event_form.description.data,
            image=db_file_path,
            status='Open',
            owner_id=current_user.id
        )
        
        db.session.add(new_event)
        db.session.commit()
        flash(f"You have successfully created a new event, '{new_event.title}'.")
        return redirect(url_for('events.show', event_id=new_event.id))

    # Error Validation
    if event_form.errors:
        # Only show the first error from the first field with errors
        first_field_errors = next(iter(event_form.errors.values()))
        first_error = first_field_errors[0] if first_field_errors else "Unknown error."
        flash(f"{first_error}")
    return render_template('events/create.html', form=event_form)

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

    # If the event doesn't exist
    if not event:
        abort(404)
    # If the user doesn't own the event
    if event.owner_id != user_id:
        abort(403)

    event_form = EventForm(obj=event, create_event=False)

    if event_form.validate_on_submit():
        db_file_path = check_upload_file(event_form)

        # If the number of available tickets was updated
        if event_form.available_tickets.data > event.available_tickets:
            event.status = "Open"

        # If the event is sold out - the number of tickets should not be reduced
        if event.status == "Sold Out":
            if event_form.available_tickets.data < event.available_tickets:
                flash("As the event is sold out, the number of tickets cannot be reduced.")
                return render_template('events/manage.html', event=event, form=event_form)

        # Setting modified fields
        event.title = event_form.title.data
        event.artist = event_form.artist.data
        event.genre = event_form.genre.data
        event.venue = event_form.venue.data
        event.location = event_form.location.data
        event.date = event_form.date.data
        event.start_time = event_form.start_time.data
        event.end_time = event_form.end_time.data
        event.available_tickets = event_form.available_tickets.data
        event.ticket_price = event_form.ticket_price.data
        event.short_description = event_form.short_description.data
        event.description = event_form.description.data

        # If the number of tickets is set to 0
        if event_form.available_tickets.data == 0:
            event.status = "Sold Out"

        # If the user did not provide a new event image
        if db_file_path != None:
            event.image = db_file_path

        # Commit the modifications
        db.session.commit()
        flash('Your event was updated successfully.')
        return redirect(url_for('events.show', event_id=event.id))

    # If the form is not valid (extra validators)
    if event_form.errors:
        # Only show the first error from the first field with errors
        first_field_errors = next(iter(event_form.errors.values()))
        first_error = first_field_errors[0] if first_field_errors else "Unknown error."
        flash(f"{first_error}")
    return render_template('events/manage.html', event=event, form=event_form)

# Register Route: Cancel Event
@events_bp.route('/manage/event-<id>/cancel')
@login_required
def cancel(id):
    event = db.session.scalar(db.select(Event).where(Event.id == id))

    if not event:
        abort(404)
    if event.owner_id != current_user.id:
        abort(403)

    if event.status == 'Open' or event.status == 'Sold Out':
        event.status = 'Cancelled'
        db.session.commit()
        flash('Your event was cancelled successfully.')
    else:
        flash('Unable to cancel event. Your event is either in the past or has previously been cancelled.')
    return redirect(url_for('events.owned_events'))