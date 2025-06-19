from flask import Blueprint, abort, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from sqlalchemy import asc
from .models import Event, Comment, Ticket, User
from .forms import EventForm, CommentForm, BookingForm, TicketForm
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
    form = EventForm(create_event=True) #create_event = true ensures correct form validators

    # create event
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
            short_description=form.short_description.data,
            description=form.description.data,
            image=db_file_path,
            status='Open',
            owner_id=current_user.id
        )
        # Commit before adding ticket information so event_id exists
        db.session.add(event)
        db.session.commit()

        # Add ticket types
        for ticket_form in form.tickets:
            ticket = Ticket(
                ticket_type=ticket_form.ticket_type.data,
                ticket_price=ticket_form.ticket_price.data,
                available_tickets=ticket_form.available_tickets.data,
                event_id=event.id
            )
            db.session.add(ticket)
        db.session.commit()
        flash('Successfully created new event')
        return redirect(url_for('events.show', event_id=event.id))

    # Error Validation - Flatten and flash all errors
    if form.errors:
        all_errors = []
        for field, errors in form.errors.items():
            if isinstance(errors, list):
                for error in errors:
                    if isinstance(error, dict):
                        for subfield, suberrors in error.items():
                            for sub_error in suberrors:
                                all_errors.append(f"{subfield}: {sub_error}")
                    else:
                        all_errors.append(f"{field}: {error}")
        flash("Form errors: " + ", ".join(all_errors))
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

    form = EventForm(obj=event)

    if form.validate_on_submit():
        """HANDLING TICKET UPDATES"""
        # Sum of existing ticket quantities (from DB)
        existing_total = sum(t.available_tickets for t in event.tickets)
        # Sum of submitted ticket quantities (from form)
        submitted_total = sum(t.form.available_tickets.data for t in form.tickets)

        existing_tickets = list(event.tickets)
        submitted_tickets = form.tickets.entries

        # Update existing tickets or create new ones
        for i, form_ticket in enumerate(submitted_tickets):
            data = form_ticket.form
            if i < len (existing_tickets):
                # Update existing ticket
                existing_tickets[i].ticket_type = data.ticket_type.data
                existing_tickets[i].available_tickets = data.available_tickets.data
                existing_tickets[i].ticket_price = data.ticket_price.data
            else:
                # Add new ticket
                new_ticket = Ticket(
                    ticket_type = data.ticket_type.data,
                    available_tickets = data.available_tickets.data,
                    ticket_price = data.ticket_price.data,
                    event_id = event.id
                )
                db.session.add(new_ticket)
        
        # Removing ticket types
        if len(existing_tickets) > len(submitted_tickets):
            for ticket in existing_tickets[len(submitted_tickets):]:
                db.session.delete(ticket)

        """HANDLING EVENT STATUS"""
        # If the number of available tickets was updated
        if (event.status == "Sold Out") and (submitted_total > existing_total):
                event.status = "Open"
            
        # If the number of tickets is set to 0
        if submitted_total == 0:
            event.status = "Sold Out"

        """HANDLING EVENT DETAILS"""
        db_file_path = check_upload_file(form)

        # Setting modified fields
        event.title = form.title.data
        event.artist = form.artist.data
        event.genre = form.genre.data
        event.venue = form.venue.data
        event.location = form.location.data
        event.date = form.date.data
        event.start_time = form.start_time.data
        event.end_time = form.end_time.data
        event.short_description = form.short_description.data
        event.description = form.description.data

        # If the user did not provide a new event image
        if db_file_path != None:
            event.image = db_file_path

        # Commit the modifications
        db.session.commit()
        flash('Event updated successfully')
        return redirect(url_for('events.show', event_id=event.id))

    # Error Validation - Flatten and flash all errors
    if form.errors:
        all_errors = []
        for field, errors in form.errors.items():
            if isinstance(errors, list):
                for error in errors:
                    if isinstance(error, dict):
                        for subfield, suberrors in error.items():
                            for sub_error in suberrors:
                                all_errors.append(f"{subfield}: {sub_error}")
                    else:
                        all_errors.append(f"{field}: {error}")
        flash("Form errors: " + ", ".join(all_errors))
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

# Adds ticket type to event creation & management forms
@events_bp.route('/get-ticket-form/<int:index>')
def get_ticket_form(index):
    form = TicketForm(prefix=f'tickets-{index}')
    return render_template('events/extra_ticket_type.html', ticket_form=form)