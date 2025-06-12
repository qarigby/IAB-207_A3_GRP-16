from flask import Blueprint, flash, render_template, request, url_for, redirect
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user
from .models import User
from .forms import LoginForm, RegisterForm
from . import db
from ozevent.utils import logout_required

# Create a blueprint - make sure all BPs have unique names
auth_bp = Blueprint('auth', __name__)

# Allows a user to login to their account
@auth_bp.route('/login', methods=['GET', 'POST'])
@logout_required
def login():
    login_form = LoginForm()

    error = None

    if login_form.validate_on_submit():
        # Assign fields from form to database object
        user_name = login_form.username.data
        password = login_form.password.data

        # Match with the user in the system
        user = db.session.scalar(db.select(User).where(User.username==user_name))

        # If the user credentials do not match the db
        if user is None:
            error = 'That username doesnt exist, please try again'
        
        # Checks password is correct
        elif not check_password_hash(user.password_hash, password): # takes the hash and cleartext password
            error = 'Incorrect password, please try again'

        # If login is successful
        if error is None:
            login_user(user)
            nextp = request.args.get('next') # this gives the url from where the login page was accessed
            print(nextp)
            if nextp is None or not nextp.startswith('/'):
                flash("Login Successful.")
                return redirect(url_for('main.index'))
            return redirect(nextp)
        else:
            flash(error)
    return render_template('user.html', form=login_form, heading='Login')

# Allows a user to register with the system
@auth_bp.route('/register', methods=['GET', 'POST'])
@logout_required
def register():
    register = RegisterForm()
    
    if (register.validate_on_submit()==True):
            #get username, password and email from the form
            uname = register.username.data
            pwd = register.password.data
            email = register.email.data
            name = register.name.data

            #check if a user exists
            user = db.session.scalar(db.select(User).where(User.username==uname))
            email_exists = db.session.scalar(db.select(User).where(User.email==email))

            if user:#this returns true when user is not None
                flash('Username already exists, please try another')
                return redirect(url_for('auth.register'))
            
            # If ther email already exists in the database
            elif email_exists:
                flash('A user with that email already exists, please use another email, or log-in to an existing account.') 
                return redirect(url_for('auth.register'))
            
            # Storing the password as a hash
            pwd_hash = generate_password_hash(pwd)

            #create a new User model object
            new_user = User(name=name, username=uname, password_hash=pwd_hash, email=email)
            db.session.add(new_user)
            db.session.commit()

            #commit to the database and redirect to HTML page
            flash("Registration Successful.")
            return redirect(url_for('auth.login'))
    
    else:
        return render_template('user.html', form=register, heading='Register')
    
# Allows a user to logout of the system
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))