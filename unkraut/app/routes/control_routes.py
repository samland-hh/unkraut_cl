# app/routes/control_routes.py
"""
Fahrzeug-Steuerung Routes
"""
from flask import Blueprint, render_template

bp = Blueprint('control', __name__)

@bp.route('/control')
def control_panel():
    """Fahrzeug-Steuerungsseite"""
    return render_template('control.html')