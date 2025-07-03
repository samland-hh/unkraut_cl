# debug_gripper_camera.py
"""
Diagnose-Script für Gripper und Kamera-Probleme
"""
import time
import subprocess
import os

def test_gripper():
    """Gripper-spezifische Tests"""
    print("🔧 Gripper-Diagnose")
    print("=" * 50)
    
    try:
        from hardware.robot_arm import robot_arm
        
        print("1. Teste alle Servos einzeln...")
        servos = ['base', 'shoulder', 'elbow', 'wrist', 'gripper', 'tool']
        
        for servo in servos:
            print(f"   Teste {servo}...")
            try:
                # Teste Bewegung von aktueller Position zu +10°
                current_pos = robot_arm.get_current_position().get(servo, 90)
                test_pos = min(180, current_pos + 10)
                
                success = robot_arm.move_joint(servo, test_pos)
                time.sleep(0.5)
                
                # Zurück zur ursprünglichen Position
                robot_arm.move_joint(servo, current_pos)
                time.sleep(0.5)
                
                print(f"      {'✅' if success else '❌'} {servo}: {'OK' if success else 'FEHLER'}")
                
            except Exception as e:
                print(f"      ❌ {servo}: Fehler - {e}")
        
        print("\n2. Gripper-spezifische Tests...")
        
        # Teste Gripper mit verschiedenen Winkeln
        test_angles = [0, 45, 90, 135, 180]
        print("   Teste Gripper-Winkel...")
        
        for angle in test_angles:
            print(f"      Gripper → {angle}°")
            try:
                success = robot_arm.move_joint('gripper', angle)
                time.sleep(1)
                
                # Prüfe ob Position wirklich gesetzt wurde
                current = robot_arm.get_current_position().get('gripper', -1)
                print(f"         Soll: {angle}°, Ist: {current}°")
                
            except Exception as e:
                print(f"         ❌ Fehler: {e}")
        
        print("\n3. Hardware-Diagnose...")
        
        # PCA9685 Kanal-Test
        try:
            from hardware.servo_controller import servo_controller
            
            print("   PCA9685 Kanäle:")
            if hasattr(servo_controller, 'pca') and servo_controller.pca:
                for channel in range(6):
                    try:
                        # Teste PWM-Signal
                        servo_controller.pca.channels[channel].duty_cycle = 0x1000  # Test-Signal
                        time.sleep(0.1)
                        servo_controller.pca.channels[channel].duty_cycle = 0
                        print(f"      Kanal {channel}: ✅ PWM OK")
                    except Exception as e:
                        print(f"      Kanal {channel}: ❌ PWM Fehler - {e}")
            else:
                print("      ⚠️  PCA9685 nicht verfügbar")
                
        except Exception as e:
            print(f"   ❌ Hardware-Test Fehler: {e}")
        
        print("\n4. Gripper-Lösungsvorschläge:")
        print("   - Prüfe Stromversorgung (Gripper braucht evtl. mehr Strom)")
        print("   - Prüfe Verkabelung am Kanal 4")
        print("   - Teste Servo an anderem Kanal")
        print("   - Prüfe Servo-Mechanik (evtl. blockiert)")
        
    except Exception as e:
        print(f"❌ Gripper-Test fehlgeschlagen: {e}")

def test_camera():
    """Kamera-Diagnose"""
    print("\n📷 Kamera-Diagnose")
    print("=" * 50)
    
    print("1. Kamera-Prozesse prüfen...")
    try:
        # Prüfe laufende libcamera-Prozesse
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        libcamera_processes = [line for line in result.stdout.split('\n') if 'libcamera' in line]
        
        if libcamera_processes:
            print("   🔍 Laufende libcamera-Prozesse gefunden:")
            for proc in libcamera_processes:
                print(f"      {proc}")
            print("   💡 Diese könnten die Kamera blockieren")
        else:
            print("   ✅ Keine blockierenden libcamera-Prozesse")
            
    except Exception as e:
        print(f"   ❌ Prozess-Check Fehler: {e}")
    
    print("\n2. Kamera-Hardware testen...")
    try:
        # Teste libcamera-hello
        result = subprocess.run(['libcamera-hello', '--list-cameras'], 
                              capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0:
            print("   ✅ libcamera-hello funktioniert")
            print(f"      Output: {result.stdout[:100]}...")
        else:
            print("   ❌ libcamera-hello Fehler")
            print(f"      Error: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("   ⚠️  libcamera-hello Timeout (evtl. OK)")
    except Exception as e:
        print(f"   ❌ libcamera-Test Fehler: {e}")
    
    print("\n3. Kamera-Module neu initialisieren...")
    try:
        # Stoppe alle Kamera-Streams
        print("   🛑 Stoppe bestehende Kamera-Streams...")
        
        # Importiere und stoppe Kamera
        from hardware.camera import camera_manager
        camera_manager.stop_stream()
        time.sleep(2)
        
        print("   🔄 Starte Kamera neu...")
        camera_manager._detect_camera()
        
        success = camera_manager.start_stream()
        print(f"   {'✅' if success else '❌'} Kamera-Neustart: {'Erfolg' if success else 'Fehler'}")
        
        if success:
            time.sleep(2)
            frame = camera_manager.get_frame()
            print(f"   📸 Frame-Test: {len(frame) if frame else 0} bytes")
        
    except Exception as e:
        print(f"   ❌ Kamera-Neustart Fehler: {e}")
    
    print("\n4. Kamera-Lösungsvorschläge:")
    print("   - Stoppe alle libcamera-Prozesse: sudo pkill libcamera")
    print("   - Neustart Kamera-Service: sudo systemctl restart camera")
    print("   - Reboot Pi: sudo reboot")
    print("   - Prüfe Kamera-Kabel")

def fix_camera():
    """Automatische Kamera-Reparatur"""
    print("\n🔧 Automatische Kamera-Reparatur")
    print("=" * 40)
    
    try:
        print("1. Stoppe libcamera-Prozesse...")
        subprocess.run(['sudo', 'pkill', '-f', 'libcamera'], timeout=5)
        time.sleep(2)
        
        print("2. Stoppe Python-Kamera-Module...")
        try:
            from hardware.camera import camera_manager
            camera_manager.stop_stream()
        except:
            pass
        
        time.sleep(2)
        
        print("3. Teste Kamera...")
        result = subprocess.run(['libcamera-hello', '--timeout', '1000'], 
                              capture_output=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Kamera-Fix erfolgreich!")
            
            # Neustart Kamera-Manager
            print("4. Starte Kamera-Manager neu...")
            from hardware.camera import camera_manager
            camera_manager._detect_camera()
            success = camera_manager.start_stream()
            
            if success:
                print("✅ Kamera-Stream wieder aktiv!")
                return True
            else:
                print("⚠️  Stream-Start teilweise erfolgreich")
                return False
        else:
            print("❌ Kamera-Hardware-Problem")
            return False
            
    except Exception as e:
        print(f"❌ Kamera-Fix Fehler: {e}")
        return False

def fix_gripper_channel():
    """Teste Gripper auf anderem Kanal"""
    print("\n🔧 Gripper-Kanal-Test")
    print("=" * 40)
    
    try:
        from hardware.robot_arm import robot_arm
        
        print("Teste Gripper auf Kanal 5 (Tool-Kanal)...")
        
        # Temporär Gripper auf Tool-Kanal testen
        servo_controller = robot_arm.servo_controller
        
        # Entferne alten Gripper
        if 'gripper' in servo_controller.servos:
            del servo_controller.servos['gripper']
        
        # Füge Gripper auf Kanal 5 hinzu
        success = servo_controller.add_servo('gripper_test', 5, default_angle=90)
        
        if success:
            print("✅ Gripper auf Kanal 5 hinzugefügt")
            
            # Teste Bewegung
            test_angles = [45, 135, 90]
            for angle in test_angles:
                servo_controller.set_servo_angle('gripper_test', angle)
                print(f"   Gripper-Test: {angle}°")
                time.sleep(1)
            
            print("💡 Falls das funktioniert: Tausche Gripper und Tool-Kabel")
            return True
        else:
            print("❌ Gripper-Test auf Kanal 5 fehlgeschlagen")
            return False
            
    except Exception as e:
        print(f"❌ Gripper-Kanal-Test Fehler: {e}")
        return False

if __name__ == '__main__':
    print("🧪 Unkraut-2025 Hardware-Diagnose")
    print("=" * 60)
    
    # Gripper-Tests
    test_gripper()
    
    # Kamera-Tests  
    test_camera()
    
    print("\n" + "=" * 60)
    print("🔧 Reparatur-Optionen:")
    print("1. Automatische Kamera-Reparatur")
    print("2. Gripper-Kanal-Test")
    print("3. Beide Reparaturen")
    
    try:
        choice = input("\nWähle Option (1/2/3) oder Enter für keine: ").strip()
        
        if choice == '1':
            fix_camera()
        elif choice == '2':
            fix_gripper_channel()
        elif choice == '3':
            fix_camera()
            time.sleep(2)
            fix_gripper_channel()
        else:
            print("Keine Reparatur gewählt")
            
    except KeyboardInterrupt:
        print("\n👋 Diagnose beendet")
    
    print("\n✅ Diagnose abgeschlossen!")
    print("💡 Starte Flask App neu: python run.py")