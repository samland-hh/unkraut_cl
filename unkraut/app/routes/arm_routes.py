# app/routes/arm_routes.py
"""
Roboterarm-Steuerung Routes
"""
from flask import Blueprint, render_template

bp = Blueprint('arm', __name__)

@bp.route('/arm')
def arm_control():
    """Roboterarm-Steuerungsseite"""
    return render_template('arm.html')