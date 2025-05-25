from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
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
            image=db_fp
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

# Check over but i think this is done