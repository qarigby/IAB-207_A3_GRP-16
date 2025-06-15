from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import Event
from . import db

# Define the homepage blueprint
main_bp = Blueprint('main', __name__)

# Home route with category filtering
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
    genres = db.session.query(Event.genre).distinct().all()
    genres = [g[0] for g in genres]

    return render_template('index.html', events=events, genres=genres)

# Register Route: Search Bar
@main_bp.route('/search')
# def search():
#     # Collect user input from search
#     search_term = request.args.get('search', '').strip()
#     if search_term:
#         # Query database for similarities
#         search_query = f"%{search_term}%"
#         event = db.session.scalars(db.select(Event).where(
#             Event.description.ilike(search_query))).first()
#         if event:
#             # Return results
#             return redirect(url_for('event.show', id=event.id))
#         flash(f"Sorry, we couldn't find any results for '{search_term}'.")
#     return redirect(url_for('main.index'))

# This search uses event names
def search():
    if request.args['search'] and request.args['search'] != "":
        print(request.args['search'])
        query = "%" + request.args['search'] + "%"
        events = db.session.scalars(db.select(Event).where(Event.name.like(query)))
        return render_template('index.html', events=events)
    else:
        return redirect(url_for('main.index'))
