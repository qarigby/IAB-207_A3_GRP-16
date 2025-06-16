from flask import Blueprint, abort, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from .models import Event, Comment
from .forms import EventForm, CommentForm
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
    form = CommentForm()
    return render_template('events/show.html', event=event, form=form, heading=event.title)

# Register Route: Post Comments on Event
@events_bp.route('/<event_id>/comment', methods=['GET', 'POST'])
@login_required
def comment(event_id):
    form = CommentForm()
    event = db.session.scalar(db.select(Event).where(Event.id == event_id))

    if form.validate_on_submit():
        print("Form submitted and validated")
        comment = Comment(
            text=form.text.data,
            event_id=event.id,
            user_id=current_user.id
        )
        db.session.add(comment)
        db.session.commit()
        flash('Your comment was successfully posted.')  

    # If GET or validation fails, show the same page again
    print("Form not validated or not a POST request")
    return render_template("events/show.html", form=form, event=event)

# Register Route: Create Event
@events_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = EventForm()

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
        flash(f"Cannot create event: {all_errors}.")
    return render_template('events/create.html', form=form)

# Register Route: Manage All Events
@events_bp.route('/manage', methods=['GET', 'POST'])
@login_required
def owned_events():
    # Select events created by the user
    events = db.session.scalars(db.select(Event).where(Event.owner_id == current_user.id)).all()
    return render_template('events/owned.html', events=events)

# Register Route: Manage Specific Event
@events_bp.route('/manage/event-<id>', methods=['GET', 'POST'])
@login_required
def manage(id):
    user_id = current_user.id
    user_event = db.session.scalar(db.select(Event).where(Event.id == id, Event.owner_id == user_id))
    event = db.session.scalar(db.select(Event).where(Event.id == id))

    if not event:
        abort(404)
    if not user_event:
        abort(403)

    form = EventForm(obj=user_event)

    if form.validate_on_submit():
        db_file_path = check_upload_file(form)
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
        event.image = db_file_path

        db.session.commit()
        flash('Event updated successfully')
        return redirect(url_for('events.owned_events'))

    if form.errors:
        all_errors = ", ".join(
            err_msg
            for field_errors in form.errors.values()
            for err_msg in field_errors
        )
        flash(f"Cannot create event: {all_errors}")
    return render_template('events/manage.html', event=user_event, form=form)

# Register Route: Cancel Event
@events_bp.route('/manage/event-<id>/cancel')
@login_required
def cancel(id):
    user_id = current_user.id
    user_event = db.session.scalar(db.select(Event).where(Event.id == id, Event.owner_id == user_id))
    event = db.session.scalar(db.select(Event).where(Event.id == id))

    if not event:
        abort(404)
    if not user_event:
        abort(403)

    if user_event.status == 'Open' or user_event.status == 'Sold Out':
        user_event.status = 'Cancelled'
        db.session.commit()
        flash('Event cancelled successfully')
    else:
        flash('Unable to cancel event. Your event is either in the past or has previously been cancelled.')
    return redirect(url_for('events.owned_events'))