# tests/debug_capture.py
"""
Debug-Script für Capture-Probleme
Testet alle Capture-Komponenten einzeln
Funktioniert aus dem tests/ Verzeichnis
"""
import os
import sys
import traceback
import time

# Python-Pfad anpassen für Imports aus dem Hauptverzeichnis
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)  # Gehe ein Verzeichnis hoch zu unkraut/
sys.path.insert(0, project_root)

print(f"🔍 Script läuft aus: {script_dir}")
print(f"📁 Projekt-Root: {project_root}")
print(f"🐍 Python-Pfad erweitert um: {project_root}")

def test_directories():
    """Teste Verzeichnis-Erstellung und -Berechtigungen"""
    print("\n📁 Teste Verzeichnisse...")
    
    # Wechsle zum Projekt-Root für Tests
    original_cwd = os.getcwd()
    os.chdir(project_root)
    print(f"📂 Arbeitsverzeichnis gewechselt zu: {os.getcwd()}")
    
    dirs_to_test = ['data', 'data/photos', 'data/images']
    
    for dir_path in dirs_to_test:
        try:
            # Verzeichnis erstellen
            os.makedirs(dir_path, exist_ok=True)
            
            # Schreibtest
            test_file = os.path.join(dir_path, 'test_write.tmp')
            with open(test_file, 'w') as f:
                f.write('test')
            
            # Datei wieder löschen
            os.remove(test_file)
            
            print(f"  ✅ {dir_path}: OK (beschreibbar)")
            
        except Exception as e:
            print(f"  ❌ {dir_path}: FEHLER - {e}")
    
    # Zurück zum ursprünglichen Verzeichnis
    os.chdir(original_cwd)

def test_camera_import():
    """Teste Kamera-Import"""
    print("\n📷 Teste Kamera-Import...")
    
    try:
        # Wechsle zum Projekt-Root für Imports
        original_cwd = os.getcwd()
        os.chdir(project_root)
        
        from hardware.camera import camera_manager
        print("  ✅ camera_manager Import: OK")
        
        # Info abrufen
        try:
            info = camera_manager.get_camera_info()
            print(f"  ✅ get_camera_info(): {info['type']}")
        except Exception as e:
            print(f"  ❌ get_camera_info(): {e}")
        
        # Frame testen
        try:
            frame = camera_manager.get_frame()
            frame_size = len(frame) if frame else 0
            print(f"  ✅ get_frame(): {frame_size} bytes")
        except Exception as e:
            print(f"  ❌ get_frame(): {e}")
        
        os.chdir(original_cwd)
        return camera_manager
        
    except Exception as e:
        print(f"  ❌ camera_manager Import: {e}")
        print(f"      Traceback: {traceback.format_exc()}")
        os.chdir(original_cwd)
        return None

def test_capture_methods(camera_manager):
    """Teste verschiedene Capture-Methoden"""
    if not camera_manager:
        print("\n❌ Kein camera_manager - überspringe Capture-Tests")
        return
    
    print("\n📸 Teste Capture-Methoden...")
    
    # Wechsle zum Projekt-Root für File-Operations
    original_cwd = os.getcwd()
    os.chdir(project_root)
    
    # Methode 1: Standard capture_image()
    print("  🧪 Methode 1: camera_manager.capture_image()")
    try:
        filename = camera_manager.capture_image("debug_test1.jpg")
        if filename:
            # Prüfe ob Datei existiert
            possible_paths = [
                f"data/photos/{filename}",
                f"data/images/{filename}",
                f"data/{filename}",
                filename
            ]
            
            file_found = False
            for path in possible_paths:
                if os.path.exists(path):
                    size = os.path.getsize(path)
                    print(f"    ✅ Datei erstellt: {path} ({size} bytes)")
                    file_found = True
                    break
            
            if not file_found:
                print(f"    ❌ Datei nicht gefunden: {filename}")
        else:
            print("    ❌ capture_image() gab None zurück")
            
    except Exception as e:
        print(f"    ❌ Fehler: {e}")
        print(f"        Traceback: {traceback.format_exc()}")
    
    # Methode 2: Frame speichern
    print("  🧪 Methode 2: Frame direkt speichern")
    try:
        frame = camera_manager.get_frame()
        if frame and len(frame) > 0:
            test_path = "data/debug_test2.jpg"
            os.makedirs("data", exist_ok=True)
            
            with open(test_path, 'wb') as f:
                f.write(frame)
            
            if os.path.exists(test_path):
                size = os.path.getsize(test_path)
                print(f"    ✅ Frame gespeichert: {test_path} ({size} bytes)")
            else:
                print("    ❌ Frame-Datei nicht erstellt")
        else:
            print(f"    ❌ Kein Frame verfügbar: {len(frame) if frame else 0} bytes")
            
    except Exception as e:
        print(f"    ❌ Fehler: {e}")
    
    # Methode 3: Mock-Frame erstellen
    print("  🧪 Methode 3: Mock-Frame erstellen")
    try:
        import cv2
        import numpy as np
        
        # Mock-Frame
        mock_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        mock_frame[:] = (50, 50, 100)
        
        cv2.putText(mock_frame, 'DEBUG TEST', (200, 240), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(mock_frame, f'from tests/', (200, 280), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
        
        test_path = "data/debug_test3.jpg"
        success = cv2.imwrite(test_path, mock_frame)
        
        if success and os.path.exists(test_path):
            size = os.path.getsize(test_path)
            print(f"    ✅ Mock-Frame erstellt: {test_path} ({size} bytes)")
        else:
            print("    ❌ Mock-Frame Erstellung fehlgeschlagen")
            
    except Exception as e:
        print(f"    ❌ Fehler: {e}")
    
    os.chdir(original_cwd)

def test_api_simulation():
    """Simuliere API-Aufruf"""
    print("\n🔌 Simuliere API-Aufruf...")
    
    original_cwd = os.getcwd()
    os.chdir(project_root)
    
    try:
        # Simuliere das was der API-Endpoint macht
        from hardware.camera import camera_manager
        
        # Verzeichnis erstellen
        os.makedirs("data/photos", exist_ok=True)
        
        # Capture versuchen
        timestamp = int(time.time())
        filename = f"api_test_{timestamp}.jpg"
        
        result = camera_manager.capture_image(filename)
        
        if result:
            # Prüfe verschiedene Pfade
            for base_dir in ["data/photos", "data/images", "data"]:
                full_path = os.path.join(base_dir, result)
                if os.path.exists(full_path):
                    size = os.path.getsize(full_path)
                    print(f"  ✅ API-Test erfolgreich: {full_path} ({size} bytes)")
                    os.chdir(original_cwd)
                    return
            
            print(f"  ❌ API-Test: Datei {result} nicht gefunden")
        else:
            print("  ❌ API-Test: capture_image() gab None zurück")
            
    except Exception as e:
        print(f"  ❌ API-Test Fehler: {e}")
        print(f"      Traceback: {traceback.format_exc()}")
    
    os.chdir(original_cwd)

def test_permissions():
    """Teste Dateiberechtigungen"""
    print("\n🔒 Teste Berechtigungen...")
    
    original_cwd = os.getcwd()
    os.chdir(project_root)
    
    try:
        import pwd
        import grp
        
        # Aktueller Benutzer
        current_user = pwd.getpwuid(os.getuid()).pw_name
        current_group = grp.getgrgid(os.getgid()).gr_name
        print(f"  👤 Läuft als: {current_user}:{current_group}")
        
        # Arbeitsverzeichnis
        cwd = os.getcwd()
        print(f"  📂 Projekt-Root: {cwd}")
        
        # Berechtigung des Arbeitsverzeichnisses
        if os.access(cwd, os.W_OK):
            print(f"  ✅ Projekt-Root beschreibbar")
        else:
            print(f"  ❌ Projekt-Root NICHT beschreibbar")
        
        # data/ Verzeichnis Berechtigung
        if os.path.exists("data"):
            if os.access("data", os.W_OK):
                print(f"  ✅ data/ Verzeichnis beschreibbar")
            else:
                print(f"  ❌ data/ Verzeichnis NICHT beschreibbar")
        
    except Exception as e:
        print(f"  ❌ Berechtigungs-Test Fehler: {e}")
    
    os.chdir(original_cwd)

def test_path_structure():
    """Teste Verzeichnisstruktur"""
    print("\n📁 Teste Verzeichnisstruktur...")
    
    expected_structure = [
        'hardware/',
        'hardware/camera.py',
        'app/',
        'app/routes/',
        'run.py'
    ]
    
    for item in expected_structure:
        path = os.path.join(project_root, item)
        if os.path.exists(path):
            print(f"  ✅ {item}: vorhanden")
        else:
            print(f"  ❌ {item}: FEHLT")

def main():
    print("🔍 Debug-Analyse für Capture-Probleme (aus tests/)")
    print("=" * 60)
    
    # System-Info
    print(f"Python: {sys.version}")
    print(f"Script-Verzeichnis: {script_dir}")
    print(f"Projekt-Root: {project_root}")
    print("")
    
    # Struktur-Test
    test_path_structure()
    
    # Tests ausführen
    test_permissions()
    test_directories()
    camera_manager = test_camera_import()
    test_capture_methods(camera_manager)
    test_api_simulation()
    
    print("\n" + "=" * 60)
    print("🎯 Debug-Analyse abgeschlossen!")
    print("\n📋 Ausführung:")
    print(f"cd {project_root}")
    print("cd tests/")
    print("python debug_capture.py")
    print("\nFalls Fehler gefunden wurden:")
    print("1. Prüfe Verzeichnis-Berechtigungen")
    print("2. Prüfe ob camera_manager korrekt startet")
    print("3. Prüfe ob Frame-Daten verfügbar sind")
    print("4. Ersetze problematischen API-Endpoint")

if __name__ == '__main__':
    main()