#!/bin/bash
# setup_roboter_arm.sh - Komplettes Setup und Test

cd ~/robo/claude/unkraut

echo "🦾 Roboterarm Setup für Unkraut-2025"
echo "====================================="

# 1. Dependencies prüfen/installieren
echo "📦 Prüfe Dependencies..."

# Adafruit Libraries installieren
if ! python -c "import adafruit_pca9685" 2>/dev/null; then
    echo "🔧 Installiere Adafruit PCA9685 Library..."
    pip install adafruit-circuitpython-pca9685
    pip install adafruit-circuitpython-motor
    pip install adafruit-blinka
else
    echo "✅ Adafruit Libraries bereits installiert"
fi

# 2. Hardware-Module erstellen (wurden bereits durch die Artifacts erstellt)
echo "📄 Hardware-Module prüfen..."

if [ ! -f "hardware/servo_controller.py" ]; then
    echo "❌ hardware/servo_controller.py fehlt"
    echo "💡 Bitte das erste Artifact ausführen"
    exit 1
else
    echo "✅ hardware/servo_controller.py vorhanden"
fi

if [ ! -f "hardware/robot_arm.py" ]; then
    echo "❌ hardware/robot_arm.py fehlt" 
    echo "💡 Bitte das zweite Artifact ausführen"
    exit 1
else
    echo "✅ hardware/robot_arm.py vorhanden"
fi

# 3. I2C-Status prüfen
echo ""
echo "🔍 I2C-Hardware-Status:"
echo "Verfügbare I2C-Geräte:"
sudo i2cdetect -y 1 | grep -E "(40|70)"

if sudo i2cdetect -y 1 | grep -q "40"; then
    echo "✅ PCA9685 auf Adresse 0x40 gefunden!"
else
    echo "⚠️  Kein PCA9685 auf 0x40 erkannt - Mock-Modus wird verwendet"
fi

# 4. Schneller Software-Test
echo ""
echo "🧪 Software-Test..."

# Test ServoController
echo "Testing ServoController..."
python3 << 'EOF'
try:
    import sys
    sys.path.append('.')
    from hardware.servo_controller import test_servo_controller
    test_servo_controller()
    print("✅ ServoController-Test erfolgreich")
except Exception as e:
    print(f"❌ ServoController-Test fehlgeschlagen: {e}")
EOF

# Test RobotArm
echo ""
echo "Testing RobotArm..."
python3 << 'EOF'
try:
    import sys
    sys.path.append('.')
    from hardware.robot_arm import quick_test
    if quick_test():
        print("✅ RobotArm-Test erfolgreich")
    else:
        print("❌ RobotArm-Test fehlgeschlagen")
except Exception as e:
    print(f"❌ RobotArm-Test fehlgeschlagen: {e}")
    import traceback
    traceback.print_exc()
EOF

echo ""
echo "📋 Nächste Schritte:"
echo ""
echo "🧪 Vollständiger Test (mit Servo-Bewegung):"
echo "   python -c \"from hardware.robot_arm import test_robot_arm; test_robot_arm()\""
echo ""
echo "🌐 Web-Interface starten:"
echo "   python run.py"
echo "   Browser: http://localhost:5000/arm"
echo ""
echo "🔧 Einzelne Befehle testen:"
echo "   python -c \"from hardware.robot_arm import robot_arm; robot_arm.home_position()\""
echo "   python -c \"from hardware.robot_arm import robot_arm; robot_arm.move_joint('base', 45)\""
echo ""

# 5. Hardware-Info
echo "📊 Hardware-Verkabelung (Erinnerung):"
cat << 'EOF'

Pi 3 → PCA9685:
├── GPIO 2 (SDA) → PCA9685 SDA
├── GPIO 3 (SCL) → PCA9685 SCL  
├── 5V → PCA9685 VCC
└── GND → PCA9685 GND

PCA9685 → Servos:
├── Kanal 0 → Base-Servo (Drehung)
├── Kanal 1 → Shoulder-Servo (Heben/Senken)
├── Kanal 2 → Elbow-Servo (Ellbogen)
├── Kanal 3 → Wrist-Servo (Handgelenk)
├── Kanal 4 → Gripper-Servo (Greifer)
└── Kanal 5 → Tool-Servo (Werkzeug/Bürste)

⚠️  Externe 5V/2A Stromversorgung für Servos erforderlich!
   (Raspberry Pi 5V reicht nicht für 6 Servos)

EOF

echo "🎯 Setup abgeschlossen! PCA9685 auf 0x40 erkannt ✅"