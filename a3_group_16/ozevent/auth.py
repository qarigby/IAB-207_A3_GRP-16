from flask import Blueprint, flash, render_template, request, url_for, redirect
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user
from .models import User
from .forms import LoginForm, RegisterForm
from . import db

# Create a blueprint - make sure all BPs have unique names
auth_bp = Blueprint('auth', __name__)

# this is a hint for a login function
@auth_bp.route('/login', methods=['GET', 'POST'])
# view function
def login():
    login_form = LoginForm()
    error = None
    if login_form.validate_on_submit():
        user_name = login_form.username.data
        password = login_form.password.data
        user = db.session.scalar(db.select(User).where(User.username==user_name))
        if user is None:
            error = 'That username doesnt exist, please try again'
        elif not check_password_hash(user.password_hash, password): # takes the hash and cleartext password
            error = 'Incorrect password, please try again'
        if error is None:
            login_user(user)
            nextp = request.args.get('next') # this gives the url from where the login page was accessed
            print(nextp)
            if nextp is None or not nextp.startswith('/'):
                return redirect(url_for('main.index'))
            return redirect(nextp)
        else:
            flash(error)
    return render_template('user.html', form=login_form, heading='Login')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    register = RegisterForm()
    #the validation of form is fine, HTTP request is POST
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
            

            # don't store the password in plaintext!
            pwd_hash = generate_password_hash(pwd)
            #create a new User model object
            new_user = User(name=name, username=uname, password_hash=pwd_hash, email=email)
            db.session.add(new_user)
            db.session.commit()
            #commit to the database and redirect to HTML page
            return redirect(url_for('auth.login'))
    #the else is called when the HTTP request calling this page is a GET
    else:
        return render_template('user.html', form=register, heading='Register')
    

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))