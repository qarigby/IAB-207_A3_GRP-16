from flask import Blueprint, abort, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from sqlalchemy import asc
from .models import Booking, Event, Comment, Ticket, User
from .forms import EventForm, CommentForm, BookingForm, TicketForm
from .utils import check_upload_file, generate_ref_code
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
    booking_form.ticket_type.choices = [(ticket.id, ticket.ticket_type) for ticket in event.tickets]
    return render_template('events/show.html', event=event, comment_form=comment_form, booking_form=booking_form)

# Booking Route: Book Tickets for an Event
@events_bp.route('/<event_id>/book', methods=['GET', 'POST'])
@login_required
def book(event_id):
    event = db.session.get(Event, event_id)
    booking_form = BookingForm()
    booking_form.ticket_type.choices = [(ticket.id, ticket.ticket_type) for ticket in event.tickets]

    # Check if the event exists
    if not event:
        abort(404)
    # Checking if the event is accepting bookings
    if event.status != "Open":
        flash('This event is not currently open for bookings.')
        return redirect(url_for('events.show', event_id=event_id))
    
    if booking_form.validate_on_submit():
        ticket = next((t for t in event.tickets if t.id == booking_form.ticket_type.data), None)
        ref_code = generate_ref_code()

        # Checking that there are enough available tickets for the booking
        if ticket and ticket.available_tickets < booking_form.num_tickets.data:
            flash('The selected ticket type does not have enough available tickets to fulfill this booking.')
            return redirect(url_for('events.show', event_id=event_id))
        
        # Removing tickets from event
        ticket.available_tickets -= booking_form.num_tickets.data
        
        # Recalculate total available tickets for the event
        total_available = sum(t.available_tickets for t in event.tickets)

        # If all ticket types are sold out, update the event status
        if total_available == 0:
            event.status = "Sold Out"
        
        # Create booking
        booking = Booking(
            ref_code = ref_code,
            num_tickets = booking_form.num_tickets.data,
            user_id = current_user.id,
            event_id = event_id,
            ticket_id = ticket.id
        )
        db.session.add(booking)
        db.session.commit()
        flash(f"Your booking was successful. The reference number for your booking is {ref_code}.")
        return redirect(url_for('events.show', event_id=event.id))
    return(redirect(url_for('events.show', event_id=event_id, booking_form=booking_form)))

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


# Delete Comment Route: Allows a user to delete their comment
@events_bp.route('/<event_id>/comments/<comment_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_comment(event_id, comment_id):
    event = db.session.get(Event, event_id)
    comment = db.session.get(Comment, comment_id)

    # If the event doesnt exist:
    if not event:
        abort(404)
    # If the comment doesnt exist:
    if not comment:
        abort(404)
    # If the user is not the author of the comment
    if current_user.id != comment.user_id:
        abort(403)

    # Delete the comment
    db.session.delete(comment)
    db.session.commit()

    flash("Comment deleted successfully.")
    return(redirect(url_for('events.show', event_id=event.id)))


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
            short_description=event_form.short_description.data,
            description=event_form.description.data,

            image=db_file_path,
            status='Open',
            owner_id=current_user.id
        )
        
        # Commit before adding ticket information so event_id exists
        db.session.add(new_event)
        db.session.commit()

        # Add ticket types
        for ticket_form in event_form.tickets:
            ticket = Ticket(
                ticket_type=ticket_form.ticket_type.data,
                ticket_price=ticket_form.ticket_price.data,
                available_tickets=ticket_form.available_tickets.data,
                event_id=new_event.id
            )
            db.session.add(ticket)
        db.session.commit()
        flash(f"You have successfully created a new event, {current_user.firstname}.")
        print(f"Event created: <title='{new_event.title}', date={new_event.date}>")
        return redirect(url_for('events.show', event_id=new_event.id))

    # Error Validation - flash the first error
    if event_form.errors:
        # Find the first error
        for field, errors in event_form.errors.items():
            if isinstance(errors, list):
                for error in errors:
                    if isinstance(error, dict):
                        # Handle nested dict structure
                        for subfield, suberrors in error.items():
                            if suberrors:
                                flash(f"{suberrors[0]}")
                                break
                    else:
                        flash(f"{error}")
                        break
            break  # Only handle the first field
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
        """HANDLING TICKET UPDATES"""
        # Sum of existing ticket quantities (from DB)
        existing_total = sum(t.available_tickets for t in event.tickets)
        # Sum of submitted ticket quantities (from form)
        submitted_total = sum(t.form.available_tickets.data for t in event_form.tickets)

        existing_tickets = list(event.tickets)
        submitted_tickets = event_form.tickets.entries

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
        # Setting modified fields
        event.title = event_form.title.data
        event.artist = event_form.artist.data
        event.genre = event_form.genre.data
        event.venue = event_form.venue.data
        event.location = event_form.location.data
        event.date = event_form.date.data
        event.start_time = event_form.start_time.data
        event.end_time = event_form.end_time.data
        event.short_description = event_form.short_description.data
        event.description = event_form.description.data

        # If the user did not provide a new event image
        if db_file_path != None:
            event.image = db_file_path

        # Commit the modifications
        db.session.commit()
        flash('Your event was updated successfully.')
        return redirect(url_for('events.show', event_id=event.id))

    # Error Validation - flash the first error
    if event_form.errors:
        # Find the first error
        for field, errors in event_form.errors.items():
            if isinstance(errors, list):
                for error in errors:
                    if isinstance(error, dict):
                        # Handle nested dict structure
                        for subfield, suberrors in error.items():
                            if suberrors:
                                flash(f"{subfield}: {suberrors[0]}")
                                break
                    else:
                        flash(f"{field}: {error}")
                        break
            break  # Only handle the first field
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

# Adds ticket type to event creation & management forms
@events_bp.route('/get-ticket-form/<int:index>')
def get_ticket_form(index):
    form = TicketForm(prefix=f'tickets-{index}')
    return render_template('events/extra_ticket_type.html', ticket_form=form)