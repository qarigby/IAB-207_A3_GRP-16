from flask import Blueprint, abort, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from .models import Event
from .forms import EventForm
from .utils import check_upload_file
from . import db 

events_bp = Blueprint('events', __name__, url_prefix='/events')

@events_bp.route('/')
def show():
    return render_template('events/show.html')

@events_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = EventForm()

    if form.validate_on_submit():
        # storing image filepath
        db_fp = check_upload_file(form)

        # Assigning database object fields
        event = Event(
            name=form.name.data,
            artist=form.artist.data,
            genre=form.genre.data,
            venue=form.venue.data,
            date=form.date.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            available_tickets=form.available_tickets.data,
            short_description=form.short_description.data,
            description=form.description.data,
            image=db_fp,
            status="open",
            user_id=current_user.id
        )

        # Add the object to the db session
        db.session.add(event)
        # Commit to the database
        db.session.commit()

        # Alert the user upon success
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
    events = db.session.scalars(db.select(Event).where(Event.user_id == current_user.id)).all()
    return render_template('events/owned.html', events=events)

@events_bp.route('/manage/event-<id>', methods=['GET', 'POST'])
@login_required
def manage(id):
    event = db.session.scalar(db.select(Event).where(Event.id == id))
    if not event:
        abort(404)

    form = EventForm(obj=event)

    if form.validate_on_submit():
        # storing image filepath
        db_fp = check_upload_file(form)
        
        event.name=form.name.data
        event.artist=form.artist.data
        event.genre=form.genre.data
        event.venue=form.venue.data
        event.date=form.date.data
        event.start_time=form.start_time.data
        event.end_time=form.end_time.data
        event.available_tickets=form.available_tickets.data
        event.short_description=form.short_description.data
        event.description=form.description.data
        event.image=db_fp

        db.session.commit()
        flash("Event updated successfully.")
        return redirect(url_for('events.owned_events'))
    
    return render_template('events/manage.html', event=event, form=form)

@events_bp.route('/manage/event-<id>/cancel')
@login_required
def cancel(id):
    event = db.session.scalar(db.select(Event).where(Event.id == id))
    if not event:
        abort(404)
    
    if event.status == 'open':
        event.status = 'cancelled'
        db.session.commit()
        flash("Event cancelled successfully.")
    else:
        flash('The event is either in the past or has previously been cancelled.')


    return redirect(url_for('events.owned_events'))

# Check over but i think this is done
# Need to make sure that the successfull redirect navigates to the event's details page
#       - Need to wait until dynamic event details pages are implemented