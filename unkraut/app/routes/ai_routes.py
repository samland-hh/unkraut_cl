# app/routes/ai_routes.py
"""
KI-Dashboard Routes
"""
from flask import Blueprint, render_template

bp = Blueprint('ai', __name__)

@bp.route('/ai')
def ai_dashboard():
    """KI-Dashboard Seite"""
    return render_template('ai.html')