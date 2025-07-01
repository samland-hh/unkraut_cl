#!/bin/bash
# Erstelle hardware/servo_controller.py

cd ~/robo/claude/unkraut

echo "📄 Erstelle hardware/servo_controller.py..."

cat > hardware/servo_controller.py << 'EOF'
# hardware/servo_controller.py
"""
PCA9685 PWM-Servo-Controller für Unkraut-2025 Roboterarm
16-Kanal PWM mit I2C Ansteuerung
"""
import time
import math

try:
    import board
    import busio
    from adafruit_pca9685 import PCA9685
    from adafruit_motor import servo
    I2C_AVAILABLE = True
    print("✅ Adafruit CircuitPython Libraries verfügbar")
except ImportError:
    I2C_AVAILABLE = False
    print("⚠️  Adafruit Libraries nicht verfügbar - Mock-Modus")

class ServoController:
    def __init__(self, i2c_address=0x40, frequency=50):
        """
        PCA9685 Servo-Controller initialisieren
        i2c_address: I2C Adresse (Standard: 0x40) - Du hast 0x40! ✅
        frequency: PWM Frequenz (Standard: 50Hz für Servos)
        """
        self.i2c_address = i2c_address
        self.frequency = frequency
        self.pca = None
        self.servos = {}
        self.servo_positions = {}
        self.servo_limits = {}
        self.is_initialized = False
        
        print(f"🔧 Initialisiere ServoController (0x{i2c_address:02x})")
        self._initialize_controller()
    
    def _initialize_controller(self):
        """PCA9685 Controller initialisieren"""
        if not I2C_AVAILABLE:
            print("🎭 Mock-ServoController initialisiert")
            self.is_initialized = True
            return True
        
        try:
            # I2C Bus initialisieren
            i2c = busio.I2C(board.SCL, board.SDA)
            
            # PCA9685 initialisieren
            self.pca = PCA9685(i2c, address=self.i2c_address)
            self.pca.frequency = self.frequency
            
            print(f"✅ PCA9685 erfolgreich initialisiert!")
            print(f"   Adresse: 0x{self.i2c_address:02x}")
            print(f"   Frequenz: {self.frequency}Hz")
            self.is_initialized = True
            return True
            
        except Exception as e:
            print(f"❌ PCA9685 Initialisierung fehlgeschlagen: {e}")
            print("🎭 Wechsle zu Mock-Modus")
            self.is_initialized = True
            return False
    
    def add_servo(self, servo_id, channel, min_angle=0, max_angle=180, 
                  min_pulse=500, max_pulse=2500, default_angle=90):
        """
        Servo zu Controller hinzufügen
        servo_id: Eindeutige ID (z.B. 'base', 'shoulder', 'elbow')
        channel: PWM Kanal (0-15)
        """
        if not I2C_AVAILABLE or not self.pca:
            # Mock-Servo
            self.servos[servo_id] = {
                'channel': channel,
                'min_angle': min_angle,
                'max_angle': max_angle,
                'mock': True
            }
            print(f"🎭 Mock-Servo '{servo_id}' auf Kanal {channel}")
        else:
            try:
                # Echtes Servo über Adafruit Library
                servo_obj = servo.Servo(
                    self.pca.channels[channel],
                    min_pulse=min_pulse,
                    max_pulse=max_pulse
                )
                
                self.servos[servo_id] = {
                    'servo': servo_obj,
                    'channel': channel,
                    'min_angle': min_angle,
                    'max_angle': max_angle,
                    'mock': False
                }
                print(f"✅ Echtes Servo '{servo_id}' auf Kanal {channel}")
            except Exception as e:
                print(f"❌ Servo '{servo_id}' Fehler: {e}")
                return False
        
        # Limits und Position speichern
        self.servo_limits[servo_id] = (min_angle, max_angle)
        self.servo_positions[servo_id] = default_angle
        
        # Auf Startposition fahren
        self.set_servo_angle(servo_id, default_angle)
        return True
    
    def set_servo_angle(self, servo_id, angle):
        """Servo auf bestimmten Winkel setzen"""
        if servo_id not in self.servos:
            print(f"❌ Servo '{servo_id}' nicht gefunden")
            return False
        
        servo_info = self.servos[servo_id]
        
        # Winkel begrenzen
        min_angle = servo_info['min_angle']
        max_angle = servo_info['max_angle']
        angle = max(min_angle, min(max_angle, angle))
        
        if servo_info.get('mock', False):
            # Mock-Servo
            print(f"🎭 Mock-Servo '{servo_id}': {angle}°")
            self.servo_positions[servo_id] = angle
            return True
        
        try:
            # Echtes Servo
            servo_info['servo'].angle = angle
            self.servo_positions[servo_id] = angle
            print(f"🦾 Servo '{servo_id}': {angle}°")
            return True
        except Exception as e:
            print(f"❌ Servo '{servo_id}' Fehler: {e}")
            return False
    
    def get_servo_angle(self, servo_id):
        """Aktuelle Servo-Position abfragen"""
        return self.servo_positions.get(servo_id, 0)
    
    def set_multiple_servos(self, servo_angles, duration=1.0):
        """Mehrere Servos gleichzeitig bewegen (interpoliert)"""
        if not servo_angles:
            return
        
        print(f"🦾 Bewege {len(servo_angles)} Servos in {duration}s")
        
        # Startpositionen sammeln
        start_positions = {}
        for servo_id in servo_angles:
            start_positions[servo_id] = self.get_servo_angle(servo_id)
        
        # Interpolation
        steps = max(10, int(duration * 20))
        step_duration = duration / steps
        
        for step in range(steps + 1):
            progress = step / steps
            # Smooth interpolation
            smooth_progress = 0.5 * (1 - math.cos(progress * math.pi))
            
            for servo_id, target_angle in servo_angles.items():
                start_angle = start_positions[servo_id]
                current_angle = start_angle + (target_angle - start_angle) * smooth_progress
                self.set_servo_angle(servo_id, current_angle)
            
            if step < steps:
                time.sleep(step_duration)
        
        print("✅ Servo-Bewegung abgeschlossen")
    
    def get_all_positions(self):
        """Alle aktuellen Servo-Positionen"""
        return self.servo_positions.copy()
    
    def disable_all_servos(self):
        """Alle Servos deaktivieren (Strom sparen)"""
        if self.pca:
            try:
                for channel in range(16):
                    self.pca.channels[channel].duty_cycle = 0
                print("🔌 Alle Servos deaktiviert")
            except Exception as e:
                print(f"❌ Servo-Deaktivierung fehlgeschlagen: {e}")
        else:
            print("🎭 Mock: Alle Servos deaktiviert")
    
    def emergency_stop(self):
        """Not-Stopp für alle Servos"""
        print("🚨 SERVO EMERGENCY STOP")
        self.disable_all_servos()
    
    def get_controller_info(self):
        """Controller-Informationen"""
        return {
            'initialized': self.is_initialized,
            'i2c_address': f"0x{self.i2c_address:02x}",
            'frequency': self.frequency,
            'servo_count': len(self.servos),
            'hardware_available': I2C_AVAILABLE and self.pca is not None,
            'servos': {
                servo_id: {
                    'channel': info['channel'],
                    'current_angle': self.servo_positions.get(servo_id, 0),
                    'limits': self.servo_limits.get(servo_id, (0, 180)),
                    'mock': info.get('mock', True)
                }
                for servo_id, info in self.servos.items()
            }
        }

# Globale Instanz
servo_controller = ServoController()

# Test-Funktion
def test_servo_controller():
    """ServoController testen"""
    print("🧪 Teste ServoController...")
    print("=" * 50)
    
    # Info anzeigen
    info = servo_controller.get_controller_info()
    print(f"Hardware verfügbar: {info['hardware_available']}")
    print(f"I2C Adresse: {info['i2c_address']}")
    print(f"Frequenz: {info['frequency']}Hz")
    
    # Test-Servo hinzufügen
    servo_controller.add_servo('test_servo', 0, default_angle=90)
    
    # Bewegungstest
    print("🧪 Teste Servo-Bewegung...")
    for angle in [0, 45, 90, 135, 180, 90]:
        print(f"Fahre zu {angle}°...")
        servo_controller.set_servo_angle('test_servo', angle)
        time.sleep(0.5)
    
    print("✅ ServoController-Test abgeschlossen")

if __name__ == '__main__':
    test_servo_controller()
EOF

echo "✅ hardware/servo_controller.py erstellt"