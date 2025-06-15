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
    img_file = form.image.data
    if img_file:
        # Sanitise filename for security
        filename = secure_filename(img_file.filename)
        # Get current path of module file
        base_path = os.path.dirname(__file__)
        # Upload file location – new directory
        upload_path = os.path.join(base_path, 'static/img', filename)
        # Store relative path in database as img location in HTML is relative
        db_upload_path = '/static/img/' + filename
        # Save file & return path
        img_file.save(upload_path)
        return db_upload_path
    return None