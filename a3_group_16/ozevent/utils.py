from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user

def logout_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            flash("You're already logged in.")
            return redirect(url_for('main.index'))  # or wherever you want to redirect
        return f(*args, **kwargs)
    return decorated_function
