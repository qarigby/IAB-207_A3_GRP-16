from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required
from .models import Event
from . import db 

events_bp = Blueprint('events', __name__, url_prefix='/events')

@events_bp.route('/')
def show():
    return render_template('events/show.html')

@events_bp.route('/create')
@login_required
def create():
    return render_template('events/create.html')