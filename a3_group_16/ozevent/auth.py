from flask import Blueprint, flash, render_template, request, url_for, redirect
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user
from .models import User
from .forms import LoginForm, RegisterForm
from . import db
from .utils import logout_required, check_upload_file

# Define Authentication Blueprint
auth_bp = Blueprint('auth', __name__)

# Register Route: Log In
@auth_bp.route('/login', methods=['GET', 'POST'])
@logout_required
def login():
    login_form = LoginForm()

    error = None

    if login_form.validate_on_submit():
        # Assign fields from form to database object
        username = login_form.username.data
        password = login_form.password.data

        # Match with the user in the system
        user = db.session.scalar(db.select(User).where(User.username==username))

        # If the user credentials do not match the db
        if user is None:
            error = 'That username does not exist, please try again'
        
        # Checks password is correct
        elif not check_password_hash(user.password_hash, password): # takes the hash and cleartext password
            error = 'Incorrect password, please try again'

        # If login is successful
        if error is None:
            login_user(user)
            nextp = request.args.get('next') # this gives the url from where the login page was accessed
            print(nextp)
            if nextp is None or not nextp.startswith('/'):
                flash('Login successful')
                return redirect(url_for('main.index'))
            return redirect(nextp)
        else:
            flash(error)
    return render_template('user.html', form=login_form, heading='Login')

# Register Route: Sign Up
@auth_bp.route('/register', methods=['GET', 'POST'])
@logout_required
def register():
    register = RegisterForm()
    
    if register.validate_on_submit():
            db_file_path = check_upload_file(register)
            # Get username, password and email from the form
            uname = register.username.data
            pwd = register.password.data
            email = register.email.data
            fname = register.firstname.data
            sname = register.surname.data
            pfp = db_file_path
            phone = register.phone_number.data
            address = register.street_address.data

            # Check if user exists
            user = db.session.scalar(db.select(User).where(User.username==uname))
            email_exists = db.session.scalar(db.select(User).where(User.email==email))

            if user: # This returns true when user is not None
                flash('Username already exists, please try another')
                return redirect(url_for('auth.register'))
            
            # If ther email already exists in the database
            elif email_exists:
                flash('A user with that email already exists, please use another email or log in to an existing account') 
                return redirect(url_for('auth.register'))
            
            # Storing the password as a hash
            pwd_hash = generate_password_hash(pwd)

            # Create new User model object
            new_user = User(username=uname, password_hash=pwd_hash, email=email, firstname=fname, surname=sname, profile_pic=pfp, phone_number=phone, street_address=address)
            db.session.add(new_user)
            db.session.commit()

            # Commit to database and redirect to HTML page
            flash(f"Registration successful, please log in to your account {uname}.")
            return redirect(url_for('auth.login'))
    # If the form is not validated
    return render_template('user.html', form=register, heading='Register')
    
# Register Route: Log Out
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))