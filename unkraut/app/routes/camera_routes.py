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