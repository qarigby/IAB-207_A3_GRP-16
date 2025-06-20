from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user
import os
from werkzeug.utils import secure_filename
from .models import Booking
from . import db

# Ensures that the user is logged out of the system
def logout_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            flash("You're already logged in.")
            return redirect(url_for('main.index')) # Redirect user back to home page if logged in
        return f(*args, **kwargs)
    return decorated_function

# Check event creation form was provided a valid file
def check_upload_file(form):
    # Retrieve image from form
    img_file = form.image.data

    if img_file:
        # Handle empty string (during event modification)
        if type(img_file) is str:
            return None
        
        # Sanitise filename for security
        filename = secure_filename(img_file.filename)

        # Retrieve directory of current module
        BASE_PATH = os.path.dirname(__file__)

        # Construct full path where file will be saved
        upload_path = os.path.join(BASE_PATH, 'static/img', filename)

        # Store relative path in database for use in HTML templates
        db_upload_path = '/static/img/' + filename
        
        # Save uploaded file & return relative path
        img_file.save(upload_path)
        return db_upload_path

    return None # No image uploaded → assume 'default_profile.png' or 'default_event.png'


def generate_ref_code():
    # Query max numeric part of ref_code (strip leading '#')
    max_reference = (
        db.session.query(Booking)
        .order_by(Booking.ref_code.desc())
        .with_entities(Booking.ref_code)
        .first()
    )
    
    if max_reference and max_reference[0]:
        # Extract number, strip '#'
        current_num = int(max_reference[0][1:])
        new_num = current_num + 1
    else:
        new_num = 1  # Start from 1 if no bookings yet

    # Format string with leading zeros, and append '#'
    new_ref_code = f"#{new_num:09d}"
    return new_ref_code