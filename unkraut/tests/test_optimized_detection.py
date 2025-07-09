# unkraut/test/test_optimized_detection.py
"""
Testet die optimierte WeedDetection mit den analysierten HSV-Werten
"""
import cv2
import numpy as np
import os
import sys
import glob
import time

# Pfad-Setup
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

def test_optimized_detection():
    """Testet die optimierte Erkennung auf allen Test-Bildern"""
    print("🎯 Test der optimierten Unkraut-Erkennung")
    print("=" * 70)
    
    try:
        from ai.weed_detection import WeedDetector
        detector = WeedDetector()
        detector.debug_mode = True
        
        print(f"🔧 Erkennungs-Einstellungen:")
        stats = detector.get_detection_stats()
        print(f"   Confidence-Threshold: {stats['confidence_threshold']}")
        print(f"   Mindestgröße: {stats['min_area']}px²")
        print(f"   Aktuelles Profil: {stats['profile_name']}")
        print(f"   HSV Lower: {stats['hsv_range']['lower']}")
        print(f"   HSV Upper: {stats['hsv_range']['upper']}")
        
        # Finde Test-Bilder
        test_dir = "test/output"
        test_images = glob.glob(os.path.join(test_dir, "test_*.jpg"))
        
        if not test_images:
            print(f"❌ Keine Test-Bilder in {test_dir} gefunden")
            return
        
        print(f"\n📁 Teste {len(test_images)} Bilder...")
        
        total_detections = 0
        total_time = 0
        results = []
        
        for image_path in sorted(test_images):
            image_name = os.path.basename(image_path)
            print(f"\n📊 Teste: {image_name}")
            print("-" * 50)
            
            # Bild laden
            image = cv2.imread(image_path)
            if image is None:
                print(f"❌ Bild konnte nicht geladen werden")
                continue
            
            # Erkennung durchführen
            start_time = time.time()
            result = detector.detect_in_image(image)
            end_time = time.time()
            
            processing_time = end_time - start_time
            detections_count = result.get('count', 0)
            confidence = result.get('confidence', 0)
            method = result.get('method', 'unknown')
            
            print(f"   ✅ Erkennungen: {detections_count}")
            print(f"   📈 Durchschnitts-Konfidenz: {confidence:.3f}")
            print(f"   ⚡ Verarbeitungszeit: {processing_time:.3f}s")
            print(f"   🛠️ Methode: {method}")
            
            # Detaillierte Ergebnisse
            detections = result.get('detections', [])
            if detections:
                print(f"   📋 Detaillierte Erkennungen:")
                for i, detection in enumerate(detections[:3]):  # Max 3 anzeigen
                    subclass = detection.get('subclass', 'unknown')
                    det_confidence = detection.get('confidence', 0)
                    area = detection.get('area', 0)
                    x = detection.get('x', 0)
                    y = detection.get('y', 0)
                    profile = detection.get('profile_used', 'unknown')
                    
                    print(f"     {i+1}. {subclass}: Konfidenz {det_confidence:.3f}, "
                          f"Größe {area}px², Position ({x}, {y})")
                    if 'mock' in detection:
                        print(f"        [MOCK-Erkennung]")
                    else:
                        print(f"        [Profil: {profile}]")
            
            # Ergebnis-Bild speichern
            if hasattr(detector, 'draw_detections') and detections_count > 0:
                marked_image = detector.draw_detections(image, detections)
                result_path = image_path.replace('test_', 'optimized_result_')
                cv2.imwrite(result_path, marked_image)
                print(f"   💾 Ergebnis gespeichert: {os.path.basename(result_path)}")
            
            # Statistiken sammeln
            total_detections += detections_count
            total_time += processing_time
            
            results.append({
                'image': image_name,
                'detections': detections_count,
                'confidence': confidence,
                'time': processing_time,
                'method': method
            })
        
        # Gesamtstatistiken
        print(f"\n📈 Gesamtstatistiken:")
        print("=" * 70)
        
        avg_detections = total_detections / len(results) if results else 0
        avg_time = total_time / len(results) if results else 0
        avg_confidence = sum(r['confidence'] for r in results) / len(results) if results else 0
        
        print(f"📊 Durchschnittliche Erkennungen pro Bild: {avg_detections:.1f}")
        print(f"📈 Durchschnittliche Konfidenz: {avg_confidence:.3f}")
        print(f"⚡ Durchschnittliche Verarbeitungszeit: {avg_time:.3f}s")
        print(f"🚀 Durchschnittliche FPS: {1/avg_time:.1f}")
        
        # Methoden-Verteilung
        methods = [r['method'] for r in results]
        opencv_count = methods.count('opencv_optimized')
        mock_count = methods.count('opencv_mock')
        
        print(f"🛠️ Methoden-Verteilung:")
        print(f"   OpenCV optimiert: {opencv_count}/{len(results)} ({opencv_count/len(results)*100:.1f}%)")
        print(f"   Mock-Erkennung: {mock_count}/{len(results)} ({mock_count/len(results)*100:.1f}%)")
        
        # Erfolgs-Bewertung
        success_rate = opencv_count / len(results) * 100 if results else 0
        
        print(f"\n🎯 Erfolgs-Bewertung:")
        if success_rate > 75:
            print(f"   ✅ AUSGEZEICHNET: {success_rate:.1f}% echte Erkennungen")
        elif success_rate > 50:
            print(f"   ✅ GUT: {success_rate:.1f}% echte Erkennungen")
        elif success_rate > 25:
            print(f"   ⚠️ BEFRIEDIGEND: {success_rate:.1f}% echte Erkennungen")
        else:
            print(f"   ❌ VERBESSERUNG NÖTIG: {success_rate:.1f}% echte Erkennungen")
        
        if avg_detections > 0:
            print(f"   ✅ Erkennungen funktionieren: Ø {avg_detections:.1f} pro Bild")
        else:
            print(f"   ❌ Keine Erkennungen - HSV-Werte prüfen")
        
        print(f"\n📁 Alle Ergebnis-Bilder in: {test_dir}/optimized_result_*.jpg")
        
        return results
        
    except Exception as e:
        print(f"❌ Test fehlgeschlagen: {e}")
        import traceback
        traceback.print_exc()
        return None

def compare_before_after():
    """Vergleicht Ergebnisse vor und nach der Optimierung"""
    print("\n🔄 Vergleich: Vorher vs. Nachher")
    print("=" * 70)
    
    # Suche alte Ergebnis-Bilder
    old_results = glob.glob("test/output/result_*.jpg")
    new_results = glob.glob("test/output/optimized_result_*.jpg")
    
    print(f"📊 Gefundene Ergebnis-Bilder:")
    print(f"   Vorher (result_*.jpg): {len(old_results)}")
    print(f"   Nachher (optimized_result_*.jpg): {len(new_results)}")
    
    if old_results and new_results:
        print(f"\n💡 Vergleiche die Bilder visuell:")
        for old_file in sorted(old_results):
            old_name = os.path.basename(old_file)
            new_name = old_name.replace('result_', 'optimized_result_')
            new_file = os.path.join('test/output', new_name)
            
            if os.path.exists(new_file):
                print(f"   📷 {old_name} vs {new_name}")

def test_specific_profiles():
    """Testet verschiedene HSV-Profile"""
    print("\n🎨 Test verschiedener HSV-Profile")
    print("=" * 70)
    
    try:
        from ai.weed_detection import WeedDetector
        
        # Test-Bild wählen
        test_image_path = "test/output/test_light_infestation.jpg"
        if not os.path.exists(test_image_path):
            print(f"❌ Test-Bild nicht gefunden: {test_image_path}")
            return
        
        image = cv2.imread(test_image_path)
        detector = WeedDetector()
        detector.debug_mode = False  # Weniger Output
        
        # Alle Profile testen
        profiles = ['bright', 'dark', 'optimized', 'fallback']
        
        print(f"📊 Teste alle Profile auf: {os.path.basename(test_image_path)}")
        
        for profile in profiles:
            print(f"\n🎯 Profil: {profile}")
            detector.change_profile(profile)
            
            result = detector.detect_in_image(image)
            detections = result.get('count', 0)
            confidence = result.get('confidence', 0)
            method = result.get('method', 'unknown')
            
            print(f"   Erkennungen: {detections}, Konfidenz: {confidence:.3f}, Methode: {method}")
        
        # Zurück zum optimierten Profil
        detector.change_profile('optimized')
        
    except Exception as e:
        print(f"❌ Profil-Test fehlgeschlagen: {e}")

def main():
    """Hauptfunktion"""
    # Teste optimierte Erkennung
    results = test_optimized_detection()
    
    # Vergleiche mit alten Ergebnissen
    compare_before_after()
    
    # Teste verschiedene Profile
    test_specific_profiles()
    
    print(f"\n✅ Optimierungs-Test abgeschlossen!")
    print(f"💡 Schaue dir die optimized_result_*.jpg Bilder an!")

if __name__ == "__main__":
    main()
