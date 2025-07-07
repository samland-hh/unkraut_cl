# tests/test_capture_fix.py
"""
Teste die reparierte Capture-Funktion
"""
import os
import sys
import time

# Python-Pfad anpassen
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)
os.chdir(project_root)

def test_capture_after_fix():
    """Teste Capture nach der Reparatur"""
    print("🔧 Teste reparierte Capture-Funktion...")
    print("=" * 50)
    
    try:
        from hardware.camera import camera_manager
        
        print(f"📷 Kamera-Typ: {camera_manager.camera_type}")
        print(f"🔄 Stream aktiv: {camera_manager.is_streaming}")
        
        # Test 1: Capture ohne Stream
        print("\n📸 Test 1: Capture ohne laufenden Stream")
        if camera_manager.is_streaming:
            camera_manager.stop_stream()
            time.sleep(1)
        
        print(f"Stream-Status vor Capture: {camera_manager.is_streaming}")
        
        filename1 = camera_manager.capture_image("test_fix_1.jpg")
        if filename1:
            # Prüfe Datei
            for base_dir in ["data/photos", "data/images", "data"]:
                filepath = os.path.join(base_dir, filename1)
                if os.path.exists(filepath):
                    size = os.path.getsize(filepath)
                    print(f"  ✅ Test 1 erfolgreich: {filepath} ({size} bytes)")
                    break
            else:
                print(f"  ❌ Test 1: Datei {filename1} nicht gefunden")
        else:
            print("  ❌ Test 1: capture_image() gab None zurück")
        
        # Test 2: Capture mit Stream
        print("\n📸 Test 2: Capture mit laufendem Stream")
        
        # Stream explizit starten
        if not camera_manager.is_streaming:
            print("🔄 Starte Stream...")
            camera_manager.start_stream()
            time.sleep(3)  # Warten bis Frames kommen
        
        print(f"Stream-Status vor Capture: {camera_manager.is_streaming}")
        frame_size = len(camera_manager.get_frame() or b"")
        print(f"Frame verfügbar: {frame_size} bytes")
        
        filename2 = camera_manager.capture_image("test_fix_2.jpg")
        if filename2:
            # Prüfe Datei
            for base_dir in ["data/photos", "data/images", "data"]:
                filepath = os.path.join(base_dir, filename2)
                if os.path.exists(filepath):
                    size = os.path.getsize(filepath)
                    print(f"  ✅ Test 2 erfolgreich: {filepath} ({size} bytes)")
                    break
            else:
                print(f"  ❌ Test 2: Datei {filename2} nicht gefunden")
        else:
            print("  ❌ Test 2: capture_image() gab None zurück")
        
        # Test 3: API-Simulation
        print("\n🔌 Test 3: API-Simulation")
        try:
            # Simuliere was die API macht
            timestamp = int(time.time())
            filename3 = f"api_simulation_{timestamp}.jpg"
            
            result = camera_manager.capture_image(filename3)
            
            if result:
                print(f"  ✅ API-Simulation erfolgreich: {result}")
                
                # Prüfe HTTP-Response-Simulation
                response_data = {
                    'status': 'captured',
                    'filename': result,
                    'timestamp': timestamp
                }
                print(f"  📡 HTTP-Response würde sein: {response_data}")
            else:
                print("  ❌ API-Simulation: capture_image() gab None zurück")
                
        except Exception as e:
            print(f"  ❌ API-Simulation Fehler: {e}")
        
        print("\n" + "=" * 50)
        print("🎯 Capture-Fix Test abgeschlossen!")
        
        # Zusammenfassung
        tests_passed = 0
        if filename1: tests_passed += 1
        if filename2: tests_passed += 1
        if 'result' in locals() and result: tests_passed += 1
        
        print(f"\n📊 Ergebnis: {tests_passed}/3 Tests bestanden")
        
        if tests_passed == 3:
            print("✅ ALLE TESTS BESTANDEN - Capture-Fix funktioniert!")
            print("\n💡 Die API sollte jetzt funktionieren:")
            print("   POST /api/camera/capture")
        elif tests_passed >= 1:
            print("⚠️  TEILWEISE ERFOLGREICH - Einige Methoden funktionieren")
        else:
            print("❌ ALLE TESTS FEHLGESCHLAGEN - Problem bleibt bestehen")
        
    except Exception as e:
        print(f"❌ Test-Fehler: {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == '__main__':
    test_capture_after_fix()