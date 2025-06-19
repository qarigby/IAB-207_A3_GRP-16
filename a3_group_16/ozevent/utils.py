from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user
import os
from werkzeug.utils import secure_filename

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