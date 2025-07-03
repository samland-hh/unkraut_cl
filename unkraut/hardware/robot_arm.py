# hardware/robot_arm.py
"""
6-DOF Roboterarm Controller für Unkraut-2025
Unterstützt PCA9685 PWM-Controller mit Mock-Fallback
"""
import time
import threading
import math

class RobotArmController:
    def __init__(self):
        self.hardware_available = False
        self.pca = None
        self.i2c_address = 0x40
        self.servo_count = 6
        self.is_moving = False
        self.emergency_stopped = False
        
        # Servo-Konfiguration
        self.servos = {
            'base': {'channel': 0, 'min_angle': 0, 'max_angle': 180, 'current': 90},
            'shoulder': {'channel': 1, 'min_angle': 0, 'max_angle': 180, 'current': 90},
            'elbow': {'channel': 2, 'min_angle': 0, 'max_angle': 180, 'current': 90},
            'wrist': {'channel': 3, 'min_angle': 0, 'max_angle': 180, 'current': 90},
            'gripper': {'channel': 5, 'min_angle': 0, 'max_angle': 180, 'current': 90},
            'tool': {'channel': 7, 'min_angle': 0, 'max_angle': 180, 'current': 0}
        }
        
        # Preset-Positionen
        self.presets = {
            'home': {
                'base': 90, 'shoulder': 90, 'elbow': 90, 
                'wrist': 90, 'gripper': 90, 'tool': 0
            },
            'weed_detect': {
                'base': 90, 'shoulder': 45, 'elbow': 45, 
                'wrist': 90, 'gripper': 180, 'tool': 0
            },
            'weed_remove': {
                'base': 90, 'shoulder': 30, 'elbow': 30, 
                'wrist': 45, 'gripper': 0, 'tool': 180
            },
            'park': {
                'base': 0, 'shoulder': 180, 'elbow': 180, 
                'wrist': 180, 'gripper': 90, 'tool': 0
            }
        }
        
        self.init_hardware()
    
    def init_hardware(self):
        """Hardware initialisieren"""
        try:
            # Versuche PCA9685 zu importieren und initialisieren
            from adafruit_pca9685 import PCA9685
            import board
            import busio
            
            # I2C Bus initialisieren
            i2c = busio.I2C(board.SCL, board.SDA)
            self.pca = PCA9685(i2c, address=self.i2c_address)
            self.pca.frequency = 50  # 50Hz für Servos
            
            self.hardware_available = True
            print("✅ Roboterarm Hardware initialisiert (PCA9685)")
            
            # Home Position fahren
            self.move_to_preset('home', duration=3.0)
            
        except ImportError:
            print("⚠️ Adafruit PCA9685 Library nicht installiert")
            print("💡 Install: pip install adafruit-circuitpython-pca9685")
            self._init_mock_mode()
        except Exception as e:
            print(f"⚠️ PCA9685 Hardware nicht verfügbar: {e}")
            self._init_mock_mode()
    
    def _init_mock_mode(self):
        """Mock-Modus initialisieren"""
        self.hardware_available = False
        self.pca = None
        print("🔧 Roboterarm Mock-Modus aktiviert")
    
    def move_joint(self, joint, angle, duration=0.5):
        """Einzelnes Gelenk bewegen"""
        if self.emergency_stopped:
            print("🚨 Roboterarm im Notaus-Modus!")
            return False
        
        if joint not in self.servos:
            print(f"❌ Unbekanntes Gelenk: {joint}")
            return False
        
        servo = self.servos[joint]
        
        # Winkel begrenzen
        angle = max(servo['min_angle'], min(servo['max_angle'], angle))
        
        if self.hardware_available and self.pca:
            try:
                # PWM-Wert berechnen (für Standard-Servos)
                pulse_length = int(500 + (angle / 180.0) * 2000)  # 500-2500µs
                duty_cycle = int(pulse_length * 65535 / 20000)    # 20ms Periode
                
                self.pca.channels[servo['channel']].duty_cycle = duty_cycle
                print(f"🦾 {joint}: {angle}° (Hardware)")
                
            except Exception as e:
                print(f"❌ Servo-Fehler {joint}: {e}")
                return False
        else:
            print(f"🔧 {joint}: {angle}° (Mock)")
        
        # Position speichern
        servo['current'] = angle
        
        # Bewegungszeit simulieren
        if duration > 0:
            time.sleep(min(duration, 0.1))  # Max 100ms für Responsivität
        
        return True
    
    def move_to_preset(self, preset_name, duration=2.0):
        """Zu Preset-Position fahren"""
        if preset_name not in self.presets:
            print(f"❌ Preset nicht gefunden: {preset_name}")
            return False
        
        preset = self.presets[preset_name]
        print(f"🎯 Fahre zu Preset: {preset_name}")
        
        self.is_moving = True
        
        try:
            # Smooth Movement Thread
            def smooth_move():
                steps = max(10, int(duration * 10))  # 10 Steps pro Sekunde
                
                # Start-Positionen
                start_positions = {joint: self.servos[joint]['current'] for joint in preset}
                
                for step in range(steps + 1):
                    if self.emergency_stopped:
                        break
                    
                    progress = step / steps
                    
                    # Interpolation für alle Gelenke
                    for joint, target_angle in preset.items():
                        if joint in start_positions:
                            start_angle = start_positions[joint]
                            current_angle = start_angle + (target_angle - start_angle) * progress
                            self.move_joint(joint, current_angle, duration=0)
                    
                    time.sleep(duration / steps)
                
                self.is_moving = False
                print(f"✅ Preset {preset_name} erreicht")
            
            thread = threading.Thread(target=smooth_move, daemon=True)
            thread.start()
            
            return True
            
        except Exception as e:
            print(f"❌ Preset-Bewegung fehlgeschlagen: {e}")
            self.is_moving = False
            return False
    
    def weed_removal_sequence(self, target_x=0, target_y=0):
        """Automatische Unkraut-Entfernung Sequenz"""
        if self.emergency_stopped:
            return False
        
        print(f"🌿 Starte Unkraut-Entfernung bei ({target_x}, {target_y})")
        
        try:
            # 1. Erkennungsposition
            self.move_to_preset('weed_detect', duration=2.0)
            time.sleep(2.0)
            
            # 2. Zielposition anfahren (vereinfacht)
            target_base = 90 + (target_x * 0.5)  # Grobe Umrechnung
            target_shoulder = 60 - (target_y * 0.3)
            
            self.move_joint('base', target_base, duration=1.0)
            time.sleep(0.5)
            self.move_joint('shoulder', target_shoulder, duration=1.0)
            time.sleep(0.5)
            
            # 3. Werkzeug positionieren
            self.move_to_preset('weed_remove', duration=1.5)
            time.sleep(1.0)
            
            # 4. Werkzeug aktivieren
            self.activate_tool(duration=3.0)
            
            # 5. Zurück zur Home-Position
            self.move_to_preset('home', duration=2.0)
            
            print("✅ Unkraut-Entfernung Sequenz abgeschlossen")
            return True
            
        except Exception as e:
            print(f"❌ Unkraut-Entfernung fehlgeschlagen: {e}")
            self.move_to_preset('home', duration=1.0)
            return False
    
    def activate_tool(self, duration=3.0):
        """Werkzeug aktivieren (Rotation/Vibration)"""
        print(f"🔧 Aktiviere Werkzeug für {duration}s")
        
        def tool_sequence():
            # Werkzeug-Servo rotieren lassen
            for cycle in range(int(duration * 2)):  # 2 Zyklen pro Sekunde
                if self.emergency_stopped:
                    break
                
                self.move_joint('tool', 180, duration=0.25)
                time.sleep(0.25)
                self.move_joint('tool', 0, duration=0.25)
                time.sleep(0.25)
            
            # Werkzeug stoppen
            self.move_joint('tool', 0, duration=0.5)
            print("🔧 Werkzeug gestoppt")
        
        thread = threading.Thread(target=tool_sequence, daemon=True)
        thread.start()
        
        return True
    
    def calibrate_servos(self):
        """Servo-Kalibrierung durchführen"""
        print("⚙️ Starte Servo-Kalibrierung...")
        
        def calibration_sequence():
            # Jedes Gelenk durch vollen Bewegungsbereich fahren
            for joint, servo in self.servos.items():
                if self.emergency_stopped:
                    break
                
                print(f"⚙️ Kalibriere {joint}...")
                
                # Zu Min-Position
                self.move_joint(joint, servo['min_angle'], duration=1.0)
                time.sleep(0.5)
                
                # Zu Max-Position
                self.move_joint(joint, servo['max_angle'], duration=2.0)
                time.sleep(0.5)
                
                # Zu Center-Position
                center = (servo['min_angle'] + servo['max_angle']) / 2
                self.move_joint(joint, center, duration=1.0)
                time.sleep(0.5)
            
            # Finale Home-Position
            self.move_to_preset('home', duration=3.0)
            print("✅ Servo-Kalibrierung abgeschlossen")
        
        thread = threading.Thread(target=calibration_sequence, daemon=True)
        thread.start()
        
        return True
    
    def emergency_stop(self):
        """Notaus - Alle Bewegungen stoppen"""
        self.emergency_stopped = True
        self.is_moving = False
        
        if self.hardware_available and self.pca:
            try:
                # Alle Servos deaktivieren
                for servo in self.servos.values():
                    self.pca.channels[servo['channel']].duty_cycle = 0
                print("🚨 Roboterarm Hardware-Notaus aktiviert")
            except:
                pass
        
        print("🚨 ROBOTERARM NOT-STOPP AKTIVIERT!")
        
        # Nach 3 Sekunden Reset erlauben
        def reset_emergency():
            time.sleep(3.0)
            self.emergency_stopped = False
            print("✅ Notaus zurückgesetzt - Roboterarm bereit")
        
        thread = threading.Thread(target=reset_emergency, daemon=True)
        thread.start()
    
    def get_current_position(self):
        """Aktuelle Position aller Gelenke"""
        return {joint: servo['current'] for joint, servo in self.servos.items()}
    
    def get_arm_info(self):
        """Vollständige Arm-Informationen"""
        return {
            'controller': {
                'hardware_available': self.hardware_available,
                'i2c_address': hex(self.i2c_address),
                'servo_count': self.servo_count,
                'is_moving': self.is_moving,
                'emergency_stopped': self.emergency_stopped
            },
            'joints': list(self.servos.keys()),
            'presets': list(self.presets.keys()),
            'current_position': self.get_current_position(),
            'servo_ranges': {
                joint: {'min': servo['min_angle'], 'max': servo['max_angle']} 
                for joint, servo in self.servos.items()
            }
        }
    
    def get_status(self):
        """Kurzer Status"""
        return {
            'available': self.hardware_available,
            'moving': self.is_moving,
            'emergency': self.emergency_stopped,
            'position': self.get_current_position()
        }

# Globale Instanz
robot_arm = RobotArmController()