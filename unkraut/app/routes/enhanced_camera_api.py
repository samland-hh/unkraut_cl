# unkraut/app/routes/enhanced_camera_api.py

import os
import json
import glob
import zipfile
import tempfile
from datetime import datetime
from flask import Blueprint, jsonify, request, send_file, Response
from app.utils.camera_handler import camera_handler

bp = Blueprint('enhanced_camera_api', __name__)

@bp.route('/api/camera/stream')
def enhanced_video_stream():
    """Enhanced Video-Stream mit System-Status-Overlay"""
    try:
        return Response(camera_handler.get_video_stream(),
                       mimetype='multipart/x-mixed-replace; boundary=frame')
    except Exception as e:
        print(f"❌ Enhanced Stream-Fehler: {e}")
        return f"Stream-Fehler: {e}", 500

@bp.route('/api/camera/toggle_overlay', methods=['POST'])
def toggle_overlay():
    """Overlay-Anzeige umschalten"""
    try:
        overlay_enabled = camera_handler.toggle_overlay()
        return jsonify({
            'status': 'success',
            'overlay_enabled': overlay_enabled,
            'message': f"Overlay {'aktiviert' if overlay_enabled else 'deaktiviert'}"
        })
    except Exception as e:
        print(f"❌ Overlay-Toggle-Fehler: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/api/camera/capture', methods=['POST'])
def enhanced_capture():
    """Enhanced Foto-Aufnahme"""
    try:
        # Custom filename aus Request holen (optional)
        data = request.get_json() if request.is_json else {}
        custom_filename = data.get('filename') if data else None
        
        filename = camera_handler.capture_image(custom_filename)
        
        if filename:
            return jsonify({
                'status': 'captured',
                'filename': filename,
                'timestamp': datetime.now().isoformat(),
                'message': f'Foto gespeichert: {filename}'
            })
        else:
            return jsonify({
                'status': 'failed',
                'error': 'Foto-Aufnahme fehlgeschlagen'
            }), 500
            
    except Exception as e:
        print(f"❌ Enhanced Capture-Fehler: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/api/camera/images')
def get_images():
    """Liste aller aufgenommenen Bilder"""
    try:
        images_dir = "data/images"
        os.makedirs(images_dir, exist_ok=True)
        
        # Alle Bildateien finden
        image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp']
        image_files = []
        
        for ext in image_extensions:
            image_files.extend(glob.glob(os.path.join(images_dir, ext)))
            image_files.extend(glob.glob(os.path.join(images_dir, ext.upper())))
        
        # Bild-Informationen sammeln
        images_info = []
        total_size = 0
        
        for filepath in sorted(image_files, key=os.path.getmtime, reverse=True):
            try:
                filename = os.path.basename(filepath)
                stat = os.stat(filepath)
                size_bytes = stat.st_size
                total_size += size_bytes
                
                images_info.append({
                    'filename': filename,
                    'size_bytes': size_bytes,
                    'size_kb': round(size_bytes / 1024, 1),
                    'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
            except Exception as e:
                print(f"❌ Bild-Info-Fehler für {filepath}: {e}")
        
        return jsonify({
            'status': 'success',
            'images': images_info,
            'total_count': len(images_info),
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'images_dir': images_dir
        })
        
    except Exception as e:
        print(f"❌ Images-List-Fehler: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/api/camera/image/<filename>')
def get_image(filename):
    """Einzelnes Bild abrufen"""
    try:
        images_dir = "data/images"
        filepath = os.path.join(images_dir, filename)
        
        # Sicherheitscheck - nur Dateien im images-Verzeichnis
        if not os.path.abspath(filepath).startswith(os.path.abspath(images_dir)):
            return "Unerlaubter Dateipfad", 403
        
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=False)
        else:
            return "Bild nicht gefunden", 404
            
    except Exception as e:
        print(f"❌ Image-Get-Fehler: {e}")
        return f"Fehler: {e}", 500

@bp.route('/api/camera/image/<filename>', methods=['DELETE'])
def delete_image(filename):
    """Einzelnes Bild löschen"""
    try:
        images_dir = "data/images"
        filepath = os.path.join(images_dir, filename)
        
        # Sicherheitscheck
        if not os.path.abspath(filepath).startswith(os.path.abspath(images_dir)):
            return jsonify({'error': 'Unerlaubter Dateipfad'}), 403
        
        if os.path.exists(filepath):
            os.remove(filepath)
            return jsonify({
                'status': 'deleted',
                'filename': filename,
                'message': f'Bild {filename} gelöscht'
            })
        else:
            return jsonify({'error': 'Bild nicht gefunden'}), 404
            
    except Exception as e:
        print(f"❌ Image-Delete-Fehler: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/api/camera/images/clear', methods=['POST'])
def clear_all_images():
    """Alle Bilder löschen"""
    try:
        images_dir = "data/images"
        
        if not os.path.exists(images_dir):
            return jsonify({
                'status': 'success',
                'deleted_count': 0,
                'message': 'Keine Bilder vorhanden'
            })
        
        # Alle Bilddateien finden und löschen
        image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp']
        deleted_count = 0
        
        for ext in image_extensions:
            files = glob.glob(os.path.join(images_dir, ext))
            files.extend(glob.glob(os.path.join(images_dir, ext.upper())))
            
            for filepath in files:
                try:
                    os.remove(filepath)
                    deleted_count += 1
                except Exception as e:
                    print(f"❌ Fehler beim Löschen von {filepath}: {e}")
        
        return jsonify({
            'status': 'success',
            'deleted_count': deleted_count,
            'message': f'{deleted_count} Bilder gelöscht'
        })
        
    except Exception as e:
        print(f"❌ Clear-Images-Fehler: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/api/camera/download_all')
def download_all_images():
    """Alle Bilder als ZIP-Datei herunterladen"""
    try:
        images_dir = "data/images"
        
        if not os.path.exists(images_dir):
            return "Keine Bilder vorhanden", 404
        
        # Temporäre ZIP-Datei erstellen
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_zip:
            with zipfile.ZipFile(temp_zip.name, 'w', zipfile.ZIP_DEFLATED) as zipf:
                
                # Alle Bilddateien zur ZIP hinzufügen
                image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp']
                file_count = 0
                
                for ext in image_extensions:
                    files = glob.glob(os.path.join(images_dir, ext))
                    files.extend(glob.glob(os.path.join(images_dir, ext.upper())))
                    
                    for filepath in files:
                        try:
                            filename = os.path.basename(filepath)
                            zipf.write(filepath, filename)
                            file_count += 1
                        except Exception as e:
                            print(f"❌ Fehler beim Hinzufügen von {filepath}: {e}")
                
                if file_count == 0:
                    return "Keine Bilder gefunden", 404
            
            # ZIP-Datei senden
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            download_name = f"unkraut_bilder_{timestamp}.zip"
            
            def cleanup_temp_file():
                try:
                    os.unlink(temp_zip.name)
                except:
                    pass
            
            # Temp-Datei nach dem Senden löschen
            import atexit
            atexit.register(cleanup_temp_file)
            
            return send_file(
                temp_zip.name,
                as_attachment=True,
                download_name=download_name,
                mimetype='application/zip'
            )
            
    except Exception as e:
        print(f"❌ Download-All-Fehler: {e}")
        return f"Download-Fehler: {e}", 500

@bp.route('/api/camera/stats')
def get_camera_stats():
    """Detaillierte Kamera-Statistiken"""
    try:
        stats = camera_handler.get_system_stats()
        
        # Zusätzliche Kamera-spezifische Stats
        images_dir = "data/images"
        image_count = 0
        total_size = 0
        
        if os.path.exists(images_dir):
            image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp']
            for ext in image_extensions:
                files = glob.glob(os.path.join(images_dir, ext))
                files.extend(glob.glob(os.path.join(images_dir, ext.upper())))
                image_count += len(files)
                
                for filepath in files:
                    try:
                        total_size += os.path.getsize(filepath)
                    except:
                        pass
        
        enhanced_stats = {
            'system': stats,
            'camera': {
                'total_images': image_count,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'overlay_enabled': camera_handler.show_overlay,
                'stream_active': True,  # Kann erweitert werden
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(enhanced_stats)
        
    except Exception as e:
        print(f"❌ Camera-Stats-Fehler: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/api/camera/settings', methods=['GET', 'POST'])
def camera_settings():
    """Kamera-Einstellungen verwalten"""
    settings_file = "data/camera_settings.json"
    
    if request.method == 'GET':
        # Einstellungen laden
        try:
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
            else:
                # Standard-Einstellungen
                settings = {
                    'resolution': '640x480',
                    'quality': 80,
                    'fps': 30,
                    'overlay_enabled': True
                }
            
            return jsonify({
                'status': 'success',
                'settings': settings
            })
            
        except Exception as e:
            print(f"❌ Settings-Load-Fehler: {e}")
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'POST':
        # Einstellungen speichern
        try:
            data = request.get_json()
            
            # Einstellungen validieren
            valid_resolutions = ['640x480', '800x600', '1024x768', '1280x720', '1920x1080']
            
            settings = {
                'resolution': data.get('resolution', '640x480'),
                'quality': max(10, min(100, data.get('quality', 80))),
                'fps': max(5, min(60, data.get('fps', 30))),
                'overlay_enabled': bool(data.get('overlay_enabled', True))
            }
            
            # Einstellungen speichern
            os.makedirs(os.path.dirname(settings_file), exist_ok=True)
            with open(settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
            
            # Overlay-Einstellung anwenden
            camera_handler.show_overlay = settings['overlay_enabled']
            
            return jsonify({
                'status': 'success',
                'settings': settings,
                'message': 'Einstellungen gespeichert'
            })
            
        except Exception as e:
            print(f"❌ Settings-Save-Fehler: {e}")
            return jsonify({'error': str(e)}), 500

# Health-Check für Enhanced Camera API
@bp.route('/api/camera/health')
def camera_health():
    """Health-Check für Kamera-System"""
    try:
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'camera_manager': camera_handler.camera_manager is not None,
            'overlay_enabled': camera_handler.show_overlay,
            'stats_monitoring': True,
            'images_directory': os.path.exists("data/images")
        }
        
        return jsonify(health_status)
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500
