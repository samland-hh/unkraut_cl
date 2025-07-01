#!/bin/bash
# camera_diagnose.sh - Kamera-Diagnose für Unkraut-2025

echo "🎥 Unkraut-2025 Kamera-Diagnose"
echo "=================================="
echo ""

# 1. System-Check
echo "📋 1. System-Informationen:"
echo "Raspberry Pi Modell: $(cat /proc/device-tree/model 2>/dev/null || echo 'Unbekannt')"
echo "OS Version: $(cat /etc/os-release | grep PRETTY_NAME | cut -d'"' -f2)"
echo "Kernel: $(uname -r)"
echo ""

# 2. Kamera-Interface Check
echo "📋 2. Kamera-Interface Status:"
if [ -f /boot/config.txt ]; then
    if grep -q "^camera_auto_detect=1" /boot/config.txt; then
        echo "✅ Kamera Auto-Detection: Aktiviert"
    else
        echo "⚠️  Kamera Auto-Detection: Nicht gefunden"
    fi
    
    if grep -q "^start_x=1" /boot/config.txt; then
        echo "✅ Legacy Kamera: Aktiviert"
    else
        echo "ℹ️  Legacy Kamera: Nicht aktiviert (normal für neue Pi OS)"
    fi
else
    echo "⚠️  /boot/config.txt nicht gefunden"
fi
echo ""

# 3. Hardware-Detection
echo "📋 3. Hardware-Erkennung:"

# libcamera Test
if command -v libcamera-hello &> /dev/null; then
    echo "✅ libcamera-apps installiert"
    echo "Verfügbare Kameras:"
    timeout 5 libcamera-hello --list-cameras 2>/dev/null | grep -E "(Available cameras|Camera)" || echo "❌ Keine libcamera Kameras gefunden"
else
    echo "❌ libcamera-apps nicht installiert"
fi
echo ""

# Legacy Pi Kamera Test
echo "Legacy Pi Kamera Status:"
vcgencmd get_camera 2>/dev/null || echo "⚠️  vcgencmd nicht verfügbar"
echo ""

# Video Devices
echo "Video Devices:"
if ls /dev/video* 2>/dev/null; then
    for device in /dev/video*; do
        echo "  📹 $device gefunden"
        # Device Info
        if command -v v4l2-ctl &> /dev/null; then
            echo "    Info: $(v4l2-ctl --device=$device --info 2>/dev/null | grep 'Card type' | cut -d: -f2 | xargs)"
        fi
    done
else
    echo "❌ Keine /dev/video* Devices gefunden"
fi
echo ""

# 4. Software-Check
echo "📋 4. Software-Dependencies:"

# Python OpenCV
if python3 -c "import cv2; print('OpenCV Version:', cv2.__version__)" 2>/dev/null; then
    echo "✅ OpenCV verfügbar"
else
    echo "❌ OpenCV nicht verfügbar"
fi

# picamera2
if python3 -c "import picamera2; print('picamera2 verfügbar')" 2>/dev/null; then
    echo "✅ picamera2 verfügbar"
else
    echo "❌ picamera2 nicht verfügbar"
fi

# numpy
if python3 -c "import numpy; print('NumPy verfügbar')" 2>/dev/null; then
    echo "✅ NumPy verfügbar"
else
    echo "❌ NumPy nicht verfügbar"
fi
echo ""

# 5. Live-Tests
echo "📋 5. Live-Tests:"

# libcamera Test
if command -v libcamera-hello &> /dev/null; then
    echo "🧪 Teste libcamera (2 Sekunden)..."
    if timeout 5 libcamera-hello --timeout 2000 2>/dev/null; then
        echo "✅ libcamera funktioniert"
    else
        echo "❌ libcamera Test fehlgeschlagen"
    fi
else
    echo "⏭️  libcamera nicht verfügbar - überspringe Test"
fi

# OpenCV Test
echo "🧪 Teste OpenCV Kamera-Zugriff..."
python3 << 'EOF'
import cv2
import sys

for device in range(3):
    try:
        cap = cv2.VideoCapture(device)
        if cap.isOpened():
            ret, frame = cap.read()
            cap.release()
            if ret:
                print(f"✅ /dev/video{device}: Funktioniert ({frame.shape[1]}x{frame.shape[0]})")
            else:
                print(f"⚠️  /dev/video{device}: Geöffnet aber kein Frame")
        else:
            print(f"❌ /dev/video{device}: Kann nicht geöffnet werden")
    except Exception as e:
        print(f"❌ /dev/video{device}: Fehler - {e}")
EOF
echo ""

# 6. Problemlösungen
echo "📋 6. Häufige Probleme & Lösungen:"
echo ""
echo "Problem: 'mmal: No data received from sensor'"
echo "Lösung:  sudo raspi-config → Interface Options → Legacy Camera → Enable"
echo ""
echo "Problem: 'Failed to create camera manager'"  
echo "Lösung:  sudo usermod -a -G video $USER && logout/login"
echo ""
echo "Problem: 'Permission denied on /dev/video0'"
echo "Lösung:  sudo chmod 666 /dev/video* oder Gruppe video beitreten"
echo ""
echo "Problem: 'libcamera-hello not found'"
echo "Lösung:  sudo apt install libcamera-apps"
echo ""

# 7. Installation Recommendations
echo "📋 7. Empfohlene Installation (falls Probleme):"
echo ""
echo "# System aktualisieren"
echo "sudo apt update && sudo apt upgrade -y"
echo ""
echo "# Kamera-Software installieren"
echo "sudo apt install -y libcamera-apps python3-opencv python3-picamera2"
echo ""
echo "# Python-Pakete"
echo "pip install opencv-python picamera2 numpy"
echo ""
echo "# Kamera aktivieren"
echo "sudo raspi-config  # → Interface Options → Camera → Enable"
echo ""
echo "# Benutzer zu video Gruppe hinzufügen"
echo "sudo usermod -a -G video \$USER"
echo ""
echo "# Neustart"
echo "sudo reboot"
echo ""

# 8. Test der Unkraut-2025 Kamera-Klasse
echo "📋 8. Teste Unkraut-2025 Kamera-Klasse:"
if [ -f "hardware/camera.py" ]; then
    echo "🧪 Führe Kamera-Test aus..."
    python3 -c "
import sys
sys.path.append('.')
from hardware.camera import camera_manager, test_all_cameras

print('Kamera-Detection:')
results = test_all_cameras()
for cam_type, available in results.items():
    status = '✅' if available else '❌'
    print(f'{status} {cam_type}: {available}')

print('\nKamera-Manager Info:')
info = camera_manager.get_camera_info()
print(f'Erkannter Typ: {info[\"type\"]}')
print(f'Verfügbare Devices: {info[\"available_devices\"]}')
"
else
    echo "❌ hardware/camera.py nicht gefunden"
    echo "Bitte erweiterte Kamera-Klasse installieren"
fi

echo ""
echo "🎯 Diagnose abgeschlossen!"
echo "Bei Problemen: Überprüfe die Lösungsvorschläge oben"