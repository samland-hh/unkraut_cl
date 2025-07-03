# 🤖 Unkraut-2025 - Vollständige Installation

## 📁 Dateistruktur (aktuell)

```
unkraut-2025/
├── app/
│   ├── __init__.py
│   └── main.py                    # ✅ Deine aktuelle main.py (All-in-One)
├── hardware/                      # ✅ NEU: Hardware-Module
│   ├── __init__.py               # ✅ Hardware-Package
│   ├── camera.py                 # ✅ Kamera-Manager
│   ├── robot_arm.py              # ✅ 6-DOF Roboterarm
│   ├── motors.py                 # ✅ Fahrzeug-Motoren
│   └── sensors.py                # ✅ Sensoren & System
├── ai/                           # ✅ NEU: KI-Module
│   ├── __init__.py               # ✅ AI-Package
│   └── weed_detection.py         # ✅ Unkrauterkennung
├── data/                         # Daten-Verzeichnisse
│   ├── images/                   # Kamera-Aufnahmen
│   ├── videos/                   # Video-Aufzeichnungen
│   └── sessions/                 # Session-Daten
├── logs/                         # Log-Dateien
├── backups/                      # Backups
├── run.py                        # ✅ Bereits vorhanden
├── requirements.txt              # ✅ Bereits vorhanden
└── README.md                     # ✅ Bereits vorhanden
```

## 🚀 Installation

### 1. Hardware-Module erstellen:
```bash
# Hardware-Verzeichnis erstellen
mkdir -p hardware ai data/{images,videos,sessions} logs backups

# Module-Dateien erstellen (aus den Artifacts kopieren):
# hardware/__init__.py
# hardware/camera.py
# hardware/robot_arm.py
# hardware/motors.py
# hardware/sensors.py
# ai/__init__.py
# ai/weed_detection.py
```

### 2. Requirements erweitern:
```bash
# requirements.txt ergänzen:
pip install opencv-python psutil adafruit-circuitpython-pca9685
```

### 3. Optional: TensorFlow für KI:
```bash
pip install tensorflow  # Für echte KI-Erkennung
```

### 4. Hardware-Pins (Optional):
```bash
# Für GPIO-Motoren:
pip install RPi.GPIO

# Für Servo-Controller:
pip install adafruit-circuitpython-pca9685
```

## 🎮 Start & Verwendung

### 1. Flask-App starten:
```bash
python run.py
# oder direkt:
python app/main.py
```

### 2. URLs:
- **Dashboard:** `http://192.168.4.1:5000/`
- **Fahrzeug-Steuerung:** `http://192.168.4.1:5000/control`
- **Roboterarm:** `http://192.168.4.1:5000/arm`
- **Kamera:** `http://192.168.4.1:5000/camera`

## 🔧 Hardware-Integration

### Kamera:
- ✅ **Automatisch:** Pi Camera oder USB-Webcam
- ✅ **Fallback:** Mock-Kamera mit bewegten Elementen
- ✅ **Stream:** MJPEG über `/api/camera/stream`

### Roboterarm:
- ✅ **Hardware:** PCA9685 PWM-Controller (I2C: 0x40)
- ✅ **Servos:** 6x Standard-Servos (0-180°)
- ✅ **Fallback:** Mock-Modus mit Logging
- ✅ **Presets:** Home, Weed-Detect, Weed-Remove

### Fahrzeug-Motoren:
- ✅ **Hardware:** L298N Motor-Driver über GPIO
- ✅ **Steuerung:** PWM-Geschwindigkeit
- ✅ **Fallback:** Mock-Modus

### Sensoren:
- ✅ **Temperatur:** DS18B20 (1-Wire)
- ✅ **System:** CPU, RAM, Temperatur
- ✅ **GPS:** Mock-Position
- ✅ **Ultraschall:** Mock-Distanzen

### KI-Erkennung:
- ✅ **OpenCV:** Grün-Erkennung für Vegetation
- ✅ **TensorFlow:** Vorbereitet für trainierte Modelle
- ✅ **Mock:** Zufällige Erkennungen für Tests

## 📱 Features

### Dashboard (`/`):
- 🎮 Schnellsteuerung (Fahrzeug + Arm)
- 📷 Live-Kamera-Stream
- 📊 System-Status
- 🔍 Ein-Klick Unkrauterkennung

### Fahrzeug-Steuerung (`/control`):
- ⬆️⬇️⬅️➡️ Richtungssteuerung
- ⚡ Geschwindigkeitsregler
- 🎮 Tastatur-Steuerung (WASD + Pfeile)
- 🛑 Not-Stopp

### Roboterarm (`/arm`):
- 🎯 Preset-Positionen (Home, Weed-Detect, etc.)
- 🎮 Manuelle Servo-Steuerung (6 Slider)
- 🤖 Automatische Unkraut-Entfernung
- 🔧 Werkzeug-Aktivierung
- ⚙️ Servo-Kalibrierung

### Kamera (`/camera`):
- 📹 Live-Stream mit Overlay
- 📸 Foto-Aufnahme
- 🔍 KI-Unkrauterkennung
- 💾 Ergebnis-Speicherung

## 🔌 API-Endpoints

### Fahrzeug:
- `POST /api/control/move` - Bewegung
- `POST /api/control/stop` - Stopp
- `GET /api/control/status` - Status

### Roboterarm:
- `POST /api/arm/move/joint` - Einzelgelenk
- `POST /api/arm/move/preset` - Preset-Position
- `POST /api/arm/emergency_stop` - Not-Stopp
- `POST /api/arm/weed_removal` - Unkraut-Sequenz
- `GET /api/arm/info` - Arm-Info

### Kamera & KI:
- `GET /api/camera/stream` - MJPEG-Stream
- `POST /api/camera/capture` - Foto
- `POST /api/ai/detect` - Unkrauterkennung

### System:
- `GET /api/system/status` - System-Status

## 💡 Mock-Modi

**Alle Module funktionieren ohne Hardware:**
- 🔧 **Kamera:** Generiert Live-Mock-Frames
- 🔧 **Roboterarm:** Loggt Bewegungen
- 🔧 **Motoren:** Simuliert Fahrzeugbewegung
- 🔧 **Sensoren:** Realistische Mock-Daten
- 🔧 **KI:** OpenCV + Zufalls-Erkennungen

## 🛜 Access Point Setup

```bash
# hostapd.conf
interface=wlan0
ssid=Unkraut-2025
hw_mode=g
channel=7
wpa=2
wpa_passphrase=unkraut123

# dnsmasq.conf
interface=wlan0
dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h

# Auto-Start Flask
sudo systemctl enable unkraut2025.service
```

**🎉 Deine main.py ist perfekt kompatibel mit allen neuen Hardware-Modulen!**