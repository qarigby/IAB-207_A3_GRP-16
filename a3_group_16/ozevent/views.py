from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import Event
from . import db 

# Create Blueprint
main_bp = Blueprint('main', __name__)

# Register Route: Landing Page
@main_bp.route('/')
def index():
    # Display events on page as they are created
    events = db.session.scalars(db.select(Event)).all()
    return render_template('index.html', events=events)

# Register Route: Search Bar
@main_bp.route('/search')
def search():
    # Collect user input from search
    search_term = request.args.get('search', '').strip()
    if search_term:
        # Query database for similarities
        search_query = f"%{search_term}%"
        event = db.session.scalars(db.select(Event).where(
            Event.description.ilike(search_query))).first()
        if event:
            # Return results
            return redirect(url_for('event.show', id=event.id))
        flash(f"Sorry, we couldn't find any results for '{search_term}'.")
    return redirect(url_for('main.index'))