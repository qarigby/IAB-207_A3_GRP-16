from flask import Blueprint, flash, render_template, request, url_for, redirect
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_login import current_user, login_user, login_required, logout_user
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

    if login_form.validate_on_submit():
        # Assign form fields to database object
        username = login_form.username.data
        password = login_form.password.data

        # Match with the user in the system
        existing_user = db.session.scalar(db.select(User).where(User.username==username))

        # If the user credentials do not match the db
        if existing_user is None:
            flash('That username does not exist. Please try again.')
        
        # Checks password is correct
        elif not check_password_hash(existing_user.password_hash, password):
            flash('The password you entered is incorrect. Please try again.')

        # If login is successful
        else:
            login_user(existing_user)
            flash(f'Welcome back, {existing_user.firstname}!')

            # Redirect user to initially requested page
            nextp = request.args.get('next') # URL of login page access point
            if nextp is None or not nextp.startswith('/'):
                return redirect(url_for('main.index'))
            return redirect(nextp)
        
    # If the login form is not validated
    return render_template('user.html', form=login_form, heading='Login')

# Register Route: Sign Up
@auth_bp.route('/register', methods=['GET', 'POST'])
@logout_required
def register():
    register_form = RegisterForm()
    
    if register_form.validate_on_submit():
            # Retrieve relative upload path for user avatar
            db_file_path = check_upload_file(register_form)

            # Get user information from the form
            uname = register_form.username.data
            pwd = register_form.password.data
            email = register_form.email.data
            fname = register_form.firstname.data
            sname = register_form.surname.data
            pfp = db_file_path
            phone = register_form.phone_number.data
            address = register_form.street_address.data

            # Scan for matches in the database
            existing_user = db.session.scalar(db.select(User).where(
            (User.username == uname) | (User.email == email) | (User.phone_number == phone)))

            # If user is located
            if existing_user:
                if existing_user.username == uname:
                    flash('An account exists with that username. Please try another.')
                elif existing_user.email == email:
                    flash('An account exists with that email. Please try another.')
                else:
                    flash('An account exists with that phone number. Please try another.')
                return render_template('user.html', form=register_form, heading='Register')
            
            # Storing the password as a hash
            pwd_hash = generate_password_hash(pwd)

            # Create new User model object
            new_user = User(username=uname, 
                            password_hash=pwd_hash, 
                            email=email, 
                            firstname=fname, 
                            surname=sname, 
                            profile_pic=pfp, 
                            phone_number=phone, 
                            street_address=address)
            db.session.add(new_user)
            db.session.commit()

            # Commit to database and redirect to HTML page
            flash(f"Registration successful. Please log in to your new account, {new_user.firstname}.")
            return redirect(url_for('auth.login'))
    
    # If the register form is not validated
    return render_template('user.html', form=register_form, heading='Register')
    
# Register Route: Log Out
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash(f"You have successfully logged out. Goodbye.")
    return redirect(url_for('main.index'))