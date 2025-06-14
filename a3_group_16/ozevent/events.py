from flask import Blueprint, abort, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from .models import Event
from .forms import EventForm
from .utils import check_upload_file
from . import db 

# ✅ Define blueprint BEFORE using it
events_bp = Blueprint('events', __name__, url_prefix='/events')

# ✅ Event details route for landing page dynamic links
@events_bp.route('/<int:event_id>')
def event_details(event_id):
    event = db.session.get(Event, event_id)
    if not event:
        abort(404)
    return render_template('events/show.html', event=event)

# Optional placeholder
@events_bp.route('/')
def show():
    return render_template('events/show.html')

@events_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = EventForm()

    if form.validate_on_submit():
        db_fp = check_upload_file(form)
        event = Event(
            name=form.name.data,
            artist=form.artist.data,
            genre=form.genre.data,
            venue=form.venue.data,
            date=form.date.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            available_tickets=form.available_tickets.data,
            ticket_price=form.ticket_price.data,
            short_description=form.short_description.data,
            description=form.description.data,
            image=db_fp,
            status="open",
            owner_id=current_user.id
        )
        db.session.add(event)
        db.session.commit()
        flash('Successfully created new event', 'success')
        return redirect(url_for('main.index'))  

    if form.errors:
        all_errors = ", ".join(
            err_msg
            for field_errors in form.errors.values()
            for err_msg in field_errors
        )
        flash(f"Cannot create event: {all_errors}")
    
    return render_template('events/create.html', form=form)

@events_bp.route('/manage', methods=['GET', 'POST'])
@login_required
def owned_events():
    # select the events that a user has created
    events = db.session.scalars(db.select(Event).where(Event.owner_id == current_user.id)).all()
    return render_template('events/owned.html', events=events)

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
        db_fp = check_upload_file(form)
        event.name = form.name.data
        event.artist = form.artist.data
        event.genre = form.genre.data
        event.venue = form.venue.data
        event.date = form.date.data
        event.start_time = form.start_time.data
        event.end_time = form.end_time.data
        event.available_tickets = form.available_tickets.data
        event.ticket_price = form.ticket_price.data
        event.short_description = form.short_description.data
        event.description = form.description.data
        event.image = db_fp

        db.session.commit()
        flash("Event updated successfully.")
        return redirect(url_for('events.owned_events'))

    if form.errors:
        all_errors = ", ".join(
            err_msg
            for field_errors in form.errors.values()
            for err_msg in field_errors
        )
        flash(f"Cannot create event: {all_errors}")
    
    return render_template('events/manage.html', event=user_event, form=form)

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

    if user_event.status == 'open':
        user_event.status = 'cancelled'
        db.session.commit()
        flash("Event cancelled successfully.")
    else:
        flash('Unable to cancel event. The event is either in the past or has previously been cancelled.')

    return redirect(url_for('events.owned_events'))
