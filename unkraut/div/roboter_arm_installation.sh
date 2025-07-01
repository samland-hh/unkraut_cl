#!/bin/bash
# install_roboter_arm.sh - PCA9685 Roboterarm Installation

echo "🦾 Unkraut-2025 Roboterarm Installation"
echo "====================================="

# 1. System-Dependencies
echo "📦 Installiere System-Dependencies..."
sudo apt update
sudo apt install -y python3-pip i2c-tools

# 2. I2C aktivieren
echo "🔧 Aktiviere I2C..."
sudo raspi-config nonint do_i2c 0

# 3. Python-Dependencies für PCA9685
echo "🐍 Installiere Python-Dependencies..."
pip install adafruit-circuitpython-pca9685
pip install adafruit-circuitpython-motor
pip install adafruit-circuitpython-servokit

# Alternative: Direkte Installation
pip install --upgrade setuptools
pip install adafruit-blinka

# 4. Teste I2C
echo "🧪 Teste I2C-Bus..."
sudo i2cdetect -y 1

# 5. Erstelle Hardware-Module
echo "📄 Erstelle Hardware-Module..."

# hardware/servo_controller.py wurde bereits im Artifact erstellt
# hardware/robot_arm.py wurde bereits im Artifact erstellt

# 6. Erweitere Flask App
echo "🌐 Erweitere Flask App..."

# Füge Roboterarm-Route zur main.py hinzu
cat >> app/main.py << 'EOF'

# Roboterarm-Integration
from app.routes import arm
app.register_blueprint(arm.bp)

@app.route('/arm')
def arm_control():
    return render_template('arm_control.html')
EOF

# 7. Erstelle Template-Datei
echo "📄 Erstelle arm_control.html Template..."
# (Template wurde im Artifact bereitgestellt)

# 8. Erweitere requirements.txt
echo "📋 Erweitere requirements.txt..."
cat >> requirements.txt << 'EOF'

# Roboterarm Dependencies
adafruit-circuitpython-pca9685==3.4.15
adafruit-circuitpython-motor==3.4.13
adafruit-circuitpython-servokit==1.3.16
adafruit-blinka==8.22.2
EOF

# 9. Erweitere Navigation
echo "🧭 Erweitere Navigation..."
# Füge Roboterarm-Link zur base.html hinzu (manuell)

echo ""
echo "✅ Roboterarm-Installation abgeschlossen!"
echo ""
echo "📋 Nächste Schritte:"
echo "1. Hardware anschließen:"
echo "   - PCA9685 an I2C (GPIO 2=SDA, GPIO 3=SCL)"
echo "   - Servos an PCA9685 Kanäle 0-5"
echo "   - 5V Stromversorgung für PCA9685"
echo ""
echo "2. Hardware testen:"
echo "   python -c \"from hardware.robot_arm import test_robot_arm; test_robot_arm()\""
echo ""
echo "3. Flask App starten:"
echo "   python run.py"
echo ""
echo "4. Browser öffnen:"
echo "   http://localhost:5000/arm"
echo ""

# Hardware-Verkabelung Diagramm
cat << 'EOF'
📊 Hardware-Verkabelung:

Raspberry Pi 3:
┌─────────────────┐
│  GPIO 2 (SDA) ──┼─── PCA9685 SDA
│  GPIO 3 (SCL) ──┼─── PCA9685 SCL  
│  5V ────────────┼─── PCA9685 VCC
│  GND ───────────┼─── PCA9685 GND
└─────────────────┘

PCA9685 (16-Kanal PWM):
┌─────────────────┐
│ Kanal 0  ───────┼─── Base-Servo
│ Kanal 1  ───────┼─── Shoulder-Servo
│ Kanal 2  ───────┼─── Elbow-Servo
│ Kanal 3  ───────┼─── Wrist-Servo
│ Kanal 4  ───────┼─── Gripper-Servo
│ Kanal 5  ───────┼─── Tool-Servo (Bürste)
│ V+  ────────────┼─── Externe 5V/6V Stromversorgung
│ GND ────────────┼─── Masse
└─────────────────┘

Servos (SG90 oder ähnlich):
- Rot/Orange: +5V (von externer Stromversorgung)
- Braun/Schwarz: GND
- Gelb/Weiß: Signal (von PCA9685)

⚠️  WICHTIG: 
- Externe Stromversorgung für Servos (min. 2A)
- Gemeinsame Masse (Pi GND + Netzteil GND)
- I2C-Adresse: 0x40 (Standard)
EOF