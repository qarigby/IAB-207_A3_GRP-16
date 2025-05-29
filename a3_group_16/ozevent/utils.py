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
            return redirect(url_for('main.index')) # redirect the user back to the home page if logged in
        return f(*args, **kwargs)
    return decorated_function

# Checks event creation form was provided a valid file
def check_upload_file(form):
  # get file data from form  
  fp = form.image.data
  filename = fp.filename
  # get the current path of the module file… store image file relative to this path  
  BASE_PATH = os.path.dirname(__file__)
  # upload file location – directory of this file/static/image
  upload_path = os.path.join(BASE_PATH,'static/img',secure_filename(filename))
  # store relative path in DB as image location in HTML is relative
  db_upload_path = '/static/img/' + secure_filename(filename)
  # save the file and return the db upload path  
  fp.save(upload_path)
  return db_upload_path