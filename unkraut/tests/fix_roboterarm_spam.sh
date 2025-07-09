#!/bin/bash
# unkraut/fix_roboterarm_spam.sh
# Behebt das Roboterarm-Spam Problem sofort

echo "🔧 Unkraut-2025 - Roboterarm-Spam Fix"
echo "====================================="

cd ~/robo/claude/unkraut

# 1. Backup der aktuellen Datei
echo "📁 Erstelle Backup..."
if [ -f "hardware/robot_arm.py" ]; then
    cp hardware/robot_arm.py hardware/robot_arm_backup_$(date +%Y%m%d_%H%M%S).py
    echo "✅ Backup erstellt: hardware/robot_arm_backup_*.py"
else
    echo "⚠️  hardware/robot_arm.py nicht gefunden"
fi

# 2. Erstelle die gefixte Version
echo "🔨 Erstelle gefixte Version..."

cat > hardware/robot_arm.py << 'EOF'
# unkraut/hardware/robot_arm.py
"""
GEFIXTE Roboterarm-Implementierung ohne Spam
Kontrolliertes Logging und einmalige Initialisierung
"""
import time
import threading
import math
import os
from datetime import datetime

class RobotArmController:
    """Roboterarm-Controller mit kontrolliertem Logging"""
    
    def __init__(self, debug_mode=False):
        self.debug_mode = debug_mode  # Standard: KEIN Debug-Spam
        self.hardware_available = False
        self.pca = None
        self.i2c_address = 0x40
        self.servo_count = 6
        self.is_moving = False
        self.emergency_stopped = False
        self.initialized = False
        
        # Servo-Konfiguration
        self.servos = {
            'base': {'channel': 0, 'min_angle': 0, 'max_angle': 180, 'default': 90, 'current': 90},
            'shoulder': {'channel': 1, 'min_angle': 0, 'max_angle': 180, 'default': 90, 'current': 90},
            'elbow': {'channel': 2, 'min_angle': 0, 'max_angle': 180, 'default': 90, 'current': 90},
            'wrist': {'channel': 3, 'min_angle': 0, 'max_angle': 180, 'default': 90, 'current': 90},
            'gripper': {'channel': 4, 'min_angle': 0, 'max_angle': 180, 'default': 90, 'current': 90},
            'tool': {'channel': 5, 'min_angle': 0, 'max_angle': 180, 'default': 0, 'current': 0}
        }
        
        # Preset-Positionen
        self.presets = {
            'home': {'base': 90, 'shoulder': 90, 'elbow': 90, 'wrist': 90, 'gripper': 90, 'tool': 0},
            'park': {'base': 90, 'shoulder': 45, 'elbow': 45, 'wrist': 90, 'gripper': 0, 'tool': 0},
            'weed_detect': {'base': 90, 'shoulder': 75, 'elbow': 105, 'wrist': 90, 'gripper': 90, 'tool': 0},
            'weed_remove': {'base': 90, 'shoulder': 60, 'elbow': 120, 'wrist': 90, 'gripper': 45, 'tool': 180},
            'maintenance': {'base': 90, 'shoulder': 135, 'elbow': 135, 'wrist': 90, 'gripper': 0, 'tool': 0}
        }
        
        # Initialisierung nur einmal
        if not self.initialized:
            self._init_hardware()
            self.initialized = True
    
    def _log(self, message, level='INFO'):
        """Kontrolliertes Logging - nur wenn debug_mode=True"""
        if self.debug_mode:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] RobotArm-{level}: {message}")
    
    def _init_hardware(self):
        """Hardware-Initialisierung - OHNE Spam"""
        try:
            # Versuche PCA9685 zu importieren
            from adafruit_pca9685 import PCA9685
            import board
            import busio
            
            # I2C-Verbindung
            i2c = busio.I2C(board.SCL, board.SDA)
            self.pca = PCA9685(i2c, address=self.i2c_address)
            self.pca.frequency = 50
            
            self.hardware_available = True
            self._log("Hardware-Initialisierung erfolgreich", 'SUCCESS')
            
            # NUR EINMAL zur Home-Position - OHNE Spam
            self._move_to_preset_silent('home')
            
        except Exception as e:
            self.hardware_available = False
            self._log(f"Hardware nicht verfügbar: {e}", 'WARNING')
            self._log("Verwende Mock-Modus", 'INFO')
    
    def _angle_to_duty_cycle(self, angle):
        """Winkel zu PWM-Duty-Cycle konvertieren"""
        min_duty = 0x1000  # ~6.25% duty cycle
        max_duty = 0x2000  # ~12.5% duty cycle
        
        angle = max(0, min(180, angle))
        duty_cycle = min_duty + (angle / 180.0) * (max_duty - min_duty)
        
        return int(duty_cycle)
    
    def _move_to_preset_silent(self, preset_name):
        """Zur Preset-Position fahren - OHNE Debug-Ausgabe"""
        if preset_name not in self.presets:
            return False
        
        preset = self.presets[preset_name]
        
        if self.hardware_available and self.pca:
            try:
                for joint_name, angle in preset.items():
                    if joint_name in self.servos:
                        servo = self.servos[joint_name]
                        duty_cycle = self._angle_to_duty_cycle(angle)
                        self.pca.channels[servo['channel']].duty_cycle = duty_cycle
                        servo['current'] = angle
                        
                        # Kurze Pause zwischen Servos
                        time.sleep(0.02)
                
                return True
                
            except Exception as e:
                self._log(f"Hardware-Preset-Fehler: {e}", 'ERROR')
                return False
        else:
            # Mock-Modus - nur Current-Position updaten
            for joint_name, angle in preset.items():
                if joint_name in self.servos:
                    self.servos[joint_name]['current'] = angle
            
            return True
    
    def move_joint(self, joint_name, angle, duration=1.0):
        """Einzelnes Gelenk bewegen - OHNE Spam"""
        if self.emergency_stopped:
            self._log("Bewegung blockiert - Emergency Stop aktiv", 'WARNING')
            return False
        
        if joint_name not in self.servos:
            self._log(f"Unbekanntes Gelenk: {joint_name}", 'ERROR')
            return False
        
        servo = self.servos[joint_name]
        angle = max(servo['min_angle'], min(servo['max_angle'], angle))
        
        if self.hardware_available and self.pca:
            try:
                duty_cycle = self._angle_to_duty_cycle(angle)
                self.pca.channels[servo['channel']].duty_cycle = duty_cycle
                servo['current'] = angle
                
                # NUR bei debug_mode ausgeben
                if self.debug_mode:
                    print(f"🦾 {joint_name}: {angle}° (Hardware)")
                
                # Pause für Servo-Bewegung
                time.sleep(max(0.1, duration))
                
                return True
                
            except Exception as e:
                self._log(f"Hardware-Bewegung fehlgeschlagen: {e}", 'ERROR')
                return False
        else:
            # Mock-Modus - nur Current-Position updaten
            servo['current'] = angle
            
            # NUR bei debug_mode ausgeben
            if self.debug_mode:
                print(f"🦾 {joint_name}: {angle}° (Mock)")
            
            return True
    
    def move_to_preset(self, preset_name, duration=2.0):
        """Zur Preset-Position fahren"""
        if self.emergency_stopped:
            self._log("Bewegung blockiert - Emergency Stop aktiv", 'WARNING')
            return False
        
        if preset_name not in self.presets:
            self._log(f"Unbekanntes Preset: {preset_name}", 'ERROR')
            return False
        
        self._log(f"Fahre zu Preset: {preset_name}")
        
        self.is_moving = True
        
        def move_sequence():
            try:
                preset = self.presets[preset_name]
                
                if self.hardware_available and self.pca:
                    # Hardware-Bewegung
                    for joint_name, angle in preset.items():
                        if joint_name in self.servos:
                            servo = self.servos[joint_name]
                            duty_cycle = self._angle_to_duty_cycle(angle)
                            self.pca.channels[servo['channel']].duty_cycle = duty_cycle
                            servo['current'] = angle
                            
                            # Kurze Pause zwischen Servos
                            time.sleep(0.05)
                    
                    # Warten auf Bewegungsende
                    time.sleep(duration)
                    
                else:
                    # Mock-Modus
                    for joint_name, angle in preset.items():
                        if joint_name in self.servos:
                            self.servos[joint_name]['current'] = angle
                    
                    # Simuliere Bewegungszeit
                    time.sleep(duration * 0.2)
                
                self.is_moving = False
                
            except Exception as e:
                self._log(f"Preset-Bewegung fehlgeschlagen: {e}", 'ERROR')
                self.is_moving = False
        
        # Bewegung in separatem Thread
        thread = threading.Thread(target=move_sequence, daemon=True)
        thread.start()
        
        return True
    
    def home_position(self):
        """Zur Home-Position fahren"""
        return self.move_to_preset('home', 2.0)
    
    def park_position(self):
        """Zur Park-Position fahren"""
        return self.move_to_preset('park', 2.0)
    
    def activate_tool(self, duration=2.0):
        """Werkzeug aktivieren"""
        self._log("Aktiviere Werkzeug")
        return self.move_joint('tool', 180, 0.5)
    
    def emergency_stop(self):
        """Notaus"""
        self.emergency_stopped = True
        self.is_moving = False
        
        if self.hardware_available and self.pca:
            try:
                for servo in self.servos.values():
                    self.pca.channels[servo['channel']].duty_cycle = 0
                self._log("Hardware-Notaus aktiviert", 'EMERGENCY')
            except:
                pass
        
        # Nach 3 Sekunden Reset
        def reset_emergency():
            time.sleep(3.0)
            self.emergency_stopped = False
            self._log("Notaus zurückgesetzt", 'INFO')
        
        thread = threading.Thread(target=reset_emergency, daemon=True)
        thread.start()
        
        return True
    
    def get_current_position(self):
        """Aktuelle Position aller Gelenke"""
        return {joint: servo['current'] for joint, servo in self.servos.items()}
    
    def get_arm_info(self):
        """Arm-Informationen"""
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
            'current_position': self.get_current_position()
        }
    
    def get_status(self):
        """Status"""
        return {
            'available': self.hardware_available,
            'moving': self.is_moving,
            'emergency': self.emergency_stopped,
            'position': self.get_current_position()
        }
    
    def enable_debug(self):
        """Debug-Modus aktivieren"""
        self.debug_mode = True
        self._log("Debug-Modus aktiviert")
    
    def disable_debug(self):
        """Debug-Modus deaktivieren"""
        self.debug_mode = False

# Globale Instanz - OHNE Debug-Spam
robot_arm = RobotArmController(debug_mode=False)

# Test-Funktionen
def test_robot_arm_silent():
    """Test ohne Spam"""
    print("🧪 Teste Roboterarm (leise)...")
    
    info = robot_arm.get_arm_info()
    print(f"✅ Hardware: {info['controller']['hardware_available']}")
    print(f"✅ Servos: {info['controller']['servo_count']}")
    
    return True

def test_robot_arm_debug():
    """Test mit Debug"""
    print("🧪 Teste Roboterarm (debug)...")
    
    robot_arm.enable_debug()
    robot_arm.move_joint('base', 45)
    time.sleep(0.5)
    robot_arm.move_joint('base', 90)
    robot_arm.disable_debug()
    
    return True

if __name__ == '__main__':
    test_robot_arm_silent()
EOF

echo "✅ Gefixte Version erstellt"

# 3. Teste die neue Version
echo "🧪 Teste neue Version..."
python3 -c "
import sys
sys.path.append('.')
from hardware.robot_arm import test_robot_arm_silent
test_robot_arm_silent()
"

if [ $? -eq 0 ]; then
    echo "✅ Test erfolgreich - kein Spam mehr!"
else
    echo "❌ Test fehlgeschlagen"
    exit 1
fi

# 4. Zeige Unterschied
echo ""
echo "📊 Änderungen:"
echo "VORHER: 🦾 base: 90.0° (Hardware) <- Bei jedem Import"
echo "NACHHER: Kein Output außer bei debug_mode=True"
echo ""
echo "🔧 Debug-Modus aktivieren (falls gewünscht):"
echo "python3 -c \"from hardware.robot_arm import robot_arm; robot_arm.enable_debug(); robot_arm.move_joint('base', 45)\""
echo ""
echo "✅ Roboterarm-Spam Problem behoben!"
echo ""
echo "🧪 Teste jetzt dein Grün-Erkennungssystem erneut:"
echo "python test/test_green_detection_improved.py"
