# Import Flask - from 'package' import 'Class'
from flask import Flask, render_template 
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from werkzeug.exceptions import HTTPException
from datetime import datetime

# Create Database
db = SQLAlchemy()

# Create Web App
def create_app():
    # Initialise Flask
    app = Flask(__name__)
    app.secret_key = 'uncrackable'
    
    # Configure/Initialise Database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ozevent.sqlite'
    db.init_app(app)

    # Initialise Bootstrap (Form Styling)
    Bootstrap5(app)

    # Initialise Bcrypt (Secure Hash)
    Bcrypt(app)
    
    # Configure/Initialise Authentication
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login' # blueprint.view_function
    login_manager.init_app(app)

    # Create User Loader Function (user_id → User)
    # Internal import prevents circular references
    from .models import User
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.scalar(db.select(User).where(User.id==user_id))

    # Register Blueprints
    from .views import main_bp
    app.register_blueprint(main_bp)
    from .events import events_bp
    app.register_blueprint(events_bp)
    from .bookings import booking_bp
    app.register_blueprint(booking_bp)
    from .auth import auth_bp
    app.register_blueprint(auth_bp)

    # Error Handling (404 & 500)
    @app.errorhandler(HTTPException)
    def handle_errors(error):
        return render_template('error.html', error=error)
    
    # Context Processing (Templates)
    @app.context_processor
    def get_context():
        year = datetime.today().year
        return dict(year=year)
    return app