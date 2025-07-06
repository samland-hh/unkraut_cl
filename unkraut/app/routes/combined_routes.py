# app/routes/combined_routes.py
"""
Kombinierte Kamera + Roboterarm Steuerung
"""
from flask import Blueprint, render_template

bp = Blueprint('combined', __name__)

@bp.route('/combined')
def combined_control():
    """Kombinierte Kamera + Roboterarm Steuerungsseite"""
    return render_template('combined.html')