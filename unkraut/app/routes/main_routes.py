# app/routes/main_routes.py
"""
Hauptrouten für Dashboard
"""
from flask import Blueprint, render_template

bp = Blueprint('main', __name__)

@bp.route('/')
def dashboard():
    """Hauptdashboard"""
    return render_template('dashboard.html')