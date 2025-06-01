from flask import Blueprint, render_template, request, redirect, url_for
from .models import Order
from . import db 

order_bp = Blueprint('order', __name__)

# need to implement this still
@order_bp.route('/booking-history')
def history():
    return render_template('booking_history.html')