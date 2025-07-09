# app/routes/camera_routes.py
"""
Kamera-Ansicht Routes
"""
from flask import Blueprint, render_template

bp = Blueprint('camera', __name__)

@bp.route('/camera')
def camera_view():
    """Kamera-Ansichtsseite"""
    return render_template('camera.html')

@bp.route('/mobile_test')
def mobile_test():
    """Mobile Test-Seite für Debugging"""
    return render_template('mobile_test.html')    