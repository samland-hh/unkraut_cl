# hardware/robot_arm.py
"""
Roboterarm-Steuerung für Unkraut-2025
Verwendet ServoController für PCA9685
"""
from .servo_controller import ServoController
import time
import math

class RobotArm:
    def __init__(self):
        """Roboterarm initialisieren"""
        print("🦾 Initialisiere RobotArm...")
        
        self.servo_controller = ServoController()
        
        # Arm-Konfiguration: 6 Servos für kompletten Roboterarm
        self.arm_config = {
            'base': {'channel': 0, 'min': 0, 'max': 180, 'default': 90},
            'shoulder': {'channel': 1, 'min': 0, 'max': 180, 'default': 90},
            'elbow': {'channel': 2, 'min': 0, 'max': 180, 'default': 90},
            'wrist': {'channel': 3, 'min': 0, 'max': 180, 'default': 90},
            'gripper': {'channel': 4, 'min': 0, 'max': 180, 'default': 90},
            'tool': {'channel': 5, 'min': 0, 'max': 180, 'default': 0}
        }
        
        # Servos konfigurieren
        self._setup_servos()
        
        # Vordefinierte Positionen für verschiedene Aufgaben
        self.preset_positions = {
            'home': {
                'base': 90, 'shoulder': 90, 'elbow': 90, 
                'wrist': 90, 'gripper': 90, 'tool': 0
            },
            'park': {
                'base': 90, 'shoulder': 45, 'elbow': 135,
                'wrist': 90, 'gripper': 180, 'tool': 0
            },
            'weed_detect': {
                'base': 90, 'shoulder': 120, 'elbow': 60,
                'wrist': 45, 'gripper': 90, 'tool': 0
            },
            'weed_remove': {
                'base': 90, 'shoulder': 135, 'elbow': 45,
                'wrist': 30, 'gripper': 45, 'tool': 180
            },
            'spray_position': {
                'base': 90, 'shoulder': 110, 'elbow': 70,
                'wrist': 0, 'gripper': 90, 'tool': 90
            },
            'collect_sample': {
                'base': 90, 'shoulder': 140, 'elbow': 40,
                'wrist': 0, 'gripper': 0, 'tool': 0
            }
        }
        
        print("✅ RobotArm initialisiert")
    
    def _setup_servos(self):
        """Alle Arm-Servos konfigurieren"""
        print("🔧 Konfiguriere Servos...")
        
        for servo_id, config in self.arm_config.items():
            success = self.servo_controller.add_servo(
                servo_id=servo_id,
                channel=config['channel'],
                min_angle=config['min'],
                max_angle=config['max'],
                default_angle=config['default']
            )
            
            if success:
                print(f"  ✅ {servo_id}: Kanal {config['channel']}")
            else:
                print(f"  ❌ {servo_id}: Fehler")
    
    def move_to_preset(self, preset_name, duration=2.0):
        """
        Zu vordefinierter Position fahren
        preset_name: Name der Position ('home', 'weed_remove', etc.)
        duration: Bewegungsdauer in Sekunden
        """
        if preset_name not in self.preset_positions:
            print(f"❌ Preset '{preset_name}' nicht gefunden")
            available = list(self.preset_positions.keys())
            print(f"Verfügbare Presets: {available}")
            return False
        
        position = self.preset_positions[preset_name]
        print(f"🦾 Fahre zu Position '{preset_name}' ({duration}s)...")
        
        self.servo_controller.set_multiple_servos(position, duration)
        return True
    
    def move_joint(self, joint_name, angle):
        """
        Einzelnes Gelenk bewegen
        joint_name: 'base', 'shoulder', 'elbow', 'wrist', 'gripper', 'tool'
        angle: Zielwinkel in Grad
        """
        if joint_name not in self.arm_config:
            print(f"❌ Gelenk '{joint_name}' nicht gefunden")
            available = list(self.arm_config.keys())
            print(f"Verfügbare Gelenke: {available}")
            return False
        
        return self.servo_controller.set_servo_angle(joint_name, angle)
    
    def get_current_position(self):
        """Aktuelle Arm-Position"""
        return self.servo_controller.get_all_positions()
    
    def set_custom_position(self, positions, duration=1.5):
        """
        Zu benutzerdefinierten Positionen fahren
        positions: Dict mit {joint_name: angle}
        """
        # Nur gültige Gelenke verwenden
        valid_positions = {}
        for joint, angle in positions.items():
            if joint in self.arm_config:
                valid_positions[joint] = angle
            else:
                print(f"⚠️  Ungültiges Gelenk ignoriert: {joint}")
        
        if valid_positions:
            print(f"🦾 Fahre zu benutzerdefinierten Positionen...")
            self.servo_controller.set_multiple_servos(valid_positions, duration)
            return True
        else:
            print("❌ Keine gültigen Positionen angegeben")
            return False
    
    def weed_removal_sequence(self, target_x=0, target_y=0):
        """
        Automatische Unkraut-Entfernung Sequenz
        target_x, target_y: Relative Position des Unkrauts
        """
        print("🌿 Starte Unkraut-Entfernung Sequenz...")
        print(f"   Ziel-Position: X={target_x}, Y={target_y}")
        
        sequence = [
            ('weed_detect', 1.5, 'Position für Erkennung'),
            ('weed_remove', 2.0, 'Zu Unkraut fahren'),
            ('tool_activate', 2.0, 'Werkzeug aktivieren'),
            ('collect_sample', 1.5, 'Sample einsammeln'),
            ('home', 2.0, 'Zurück zur Home-Position')
        ]
        
        for step, (action, duration, description) in enumerate(sequence, 1):
            print(f"  {step}/5: {description}")
            
            if action == 'tool_activate':
                self.activate_tool(duration)
            else:
                self.move_to_preset(action, duration)
            
            time.sleep(0.5)  # Kurze Pause zwischen Bewegungen
        
        print("✅ Unkraut-Entfernung Sequenz abgeschlossen")
    
    def activate_tool(self, duration=2.0):
        """
        Werkzeug aktivieren (Bürste rotieren oder Spray)
        """
        print(f"🔧 Aktiviere Werkzeug für {duration}s...")
        
        start_angle = self.servo_controller.get_servo_angle('tool')
        
        # Tool-Servo oszillieren lassen (Bürste simulieren)
        steps = int(duration * 10)  # 10 Steps pro Sekunde
        for i in range(steps):
            # Oszillations-Bewegung
            angle = start_angle + 30 * math.sin(i * 0.8)
            self.servo_controller.set_servo_angle('tool', angle)
            time.sleep(0.1)
        
        # Zurück zur Ruheposition
        self.servo_controller.set_servo_angle('tool', start_angle)
        print("🔧 Werkzeug deaktiviert")
    
    def emergency_stop(self):
        """Not-Stopp für Roboterarm"""
        print("🚨 ROBOTERARM EMERGENCY STOP")
        self.servo_controller.emergency_stop()
    
    def home_position(self):
        """Zur Home-Position fahren"""
        print("🏠 Fahre zur Home-Position...")
        return self.move_to_preset('home', 2.0)
    
    def park_position(self):
        """Zur Park-Position fahren (Strom sparen)"""
        print("🚗 Fahre zur Park-Position...")
        result = self.move_to_preset('park', 2.0)
        time.sleep(2.5)
        print("🔌 Deaktiviere alle Servos...")
        self.servo_controller.disable_all_servos()
        return result
    
    def get_arm_info(self):
        """Roboterarm-Informationen"""
        controller_info = self.servo_controller.get_controller_info()
        
        return {
            'controller': controller_info,
            'joints': list(self.arm_config.keys()),
            'presets': list(self.preset_positions.keys()),
            'current_position': self.get_current_position(),
            'joint_limits': {
                joint: (config['min'], config['max']) 
                for joint, config in self.arm_config.items()
            }
        }
    
    def calibrate_servos(self):
        """
        Servo-Kalibrierung durchführen
        Fährt alle Servos durch ihren Bewegungsbereich
        """
        print("🔧 Starte Servo-Kalibrierung...")
        
        for joint_name in self.arm_config:
            config = self.arm_config[joint_name]
            print(f"  🔧 Kalibriere {joint_name}...")
            
            # Minimum Position
            self.move_joint(joint_name, config['min'])
            time.sleep(1)
            
            # Maximum Position  
            self.move_joint(joint_name, config['max'])
            time.sleep(1)
            
            # Zurück zu Default
            self.move_joint(joint_name, config['default'])
            time.sleep(0.5)
        
        print("✅ Servo-Kalibrierung abgeschlossen")
        return self.home_position()

# Globale Instanz
robot_arm = RobotArm()

# Test-Funktionen
def test_robot_arm():
    """Ausführlicher Roboterarm-Test"""
    print("🧪 Teste Roboterarm...")
    print("=" * 50)
    
    # Info anzeigen
    info = robot_arm.get_arm_info()
    print(f"Controller: {info['controller']['hardware_available']}")
    print(f"Gelenke: {info['joints']}")
    print(f"Presets: {info['presets']}")
    print(f"Servo-Anzahl: {info['controller']['servo_count']}")
    
    # Kurze Kalibrierung (nur ein Servo)
    print("\n🔧 Kurze Kalibrierung...")
    robot_arm.move_joint('base', 45)
    time.sleep(1)
    robot_arm.move_joint('base', 135)
    time.sleep(1)
    robot_arm.move_joint('base', 90)
    time.sleep(1)
    
    # Preset-Test
    print("\n🎯 Teste Preset-Positionen...")
    presets_to_test = ['home', 'weed_detect', 'weed_remove']
    
    for preset in presets_to_test:
        print(f"  🦾 Teste: {preset}")
        robot_arm.move_to_preset(preset, 1.0)
        time.sleep(1.5)
    
    # Zurück zu Home
    robot_arm.home_position()
    time.sleep(2)
    
    # Tool-Test
    print("\n🔧 Teste Werkzeug...")
    robot_arm.activate_tool(2.0)
    
    print("\n✅ Roboterarm-Test abgeschlossen!")
    print("💡 Für Web-Interface: python run.py")

def quick_test():
    """Schneller Test ohne Bewegung"""
    print("⚡ Schneller Roboterarm-Test...")
    
    info = robot_arm.get_arm_info()
    print(f"✅ Hardware: {info['controller']['hardware_available']}")
    print(f"✅ Servos: {info['controller']['servo_count']}")
    print(f"✅ I2C: {info['controller']['i2c_address']}")
    
    return True

if __name__ == '__main__':
    test_robot_arm()
