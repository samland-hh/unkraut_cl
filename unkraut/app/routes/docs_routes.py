# app/routes/docs_routes.py
"""
Dokumentation Routes
"""
from flask import Blueprint, render_template, send_from_directory, abort
import os
import glob

bp = Blueprint('docs', __name__)

@bp.route('/docs')
def docs_index():
    """Dokumentation Index Seite"""
    docs_dir = os.path.join(os.getcwd(), 'docs')
    html_files = []
    
    if os.path.exists(docs_dir):
        # Suche nach HTML-Dateien im docs Verzeichnis
        pattern = os.path.join(docs_dir, '*.html')
        for file_path in glob.glob(pattern):
            filename = os.path.basename(file_path)
            # Erstelle eine schöne Bezeichnung aus dem Dateinamen
            display_name = filename.replace('.html', '').replace('_', ' ').replace('-', ' ').title()
            html_files.append({
                'filename': filename,
                'display_name': display_name,
                'path': f'/docs/view/{filename}'
            })
    
    return render_template('docs.html', html_files=html_files)

@bp.route('/docs/view/<filename>')
def view_doc(filename):
    """Zeige spezifische HTML-Dokumentation"""
    docs_dir = os.path.join(os.getcwd(), 'docs')
    
    # Sicherheitsprüfung - nur .html Dateien erlauben
    if not filename.endswith('.html'):
        abort(404)
    
    file_path = os.path.join(docs_dir, filename)
    
    if not os.path.exists(file_path):
        abort(404)
    
    try:
        return send_from_directory(docs_dir, filename)
    except Exception:
        abort(404)