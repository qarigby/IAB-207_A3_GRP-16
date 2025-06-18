from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy import or_
from .models import Event
from . import db

# Define Homepage Blueprint
main_bp = Blueprint('main', __name__)

# Regiser Route: Home (Category Filtering)
@main_bp.route('/')
def index():
    # Get events from db
    dt_now = datetime.now().date()
    events = Event.query.all()

    for event in events:
        if event.date < dt_now and event.status != 'Inactive':
            event.status = 'Inactive'
            db.session.commit()

    # Get distinct genres for the dropdown
    genres = db.session.query(Event.genre).filter(Event.status == "Open").distinct().all()
    genres = [g[0] for g in genres]

    return render_template('index.html', events=events, genres=genres)

# Register Route: Search Bar
@main_bp.route('/search')
def search():
    # Collect user input from search
    search_term = request.args.get('search', '').strip()
    if search_term:
        # Query database for similarities
        search_query = f"%{search_term}%"
        events = db.session.scalars(db.select(Event).where(
            or_(
                Event.title.ilike(search_query), # case-insensitive
                Event.description.ilike(search_query),
                Event.artist.ilike(search_query),
                Event.genre.ilike(search_query),
                Event.venue.ilike(search_query)
            ))).all()
        # Return results
        return render_template('index.html', events=events, search_term=search_term)
    return redirect(url_for('main.index'))