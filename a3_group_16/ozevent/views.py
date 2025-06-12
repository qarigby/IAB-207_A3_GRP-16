from flask import Blueprint, render_template, request
from .models import Event
from . import db

# Define the homepage blueprint
main_bp = Blueprint('main', __name__)

# Home route with category filtering
@main_bp.route('/')
def index():
    genre_filter = request.args.get('genre')

    if genre_filter:
        events = Event.query.filter_by(genre=genre_filter).all()
    else:
        events = Event.query.all()

    # Get distinct genres for the dropdown
    genres = db.session.query(Event.genre).distinct().all()
    genres = [g[0] for g in genres]  # Flatten

    return render_template('index.html', events=events, genres=genres, selected_genre=genre_filter)
