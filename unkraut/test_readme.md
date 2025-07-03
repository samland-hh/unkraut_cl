# 🧪 Unkraut-2025 Test Suite

## 📋 Übersicht

Umfassende Test-Suite für alle Komponenten des Unkraut-2025 Systems:
- **Web-Interface Tests** - Alle Seiten erreichbar
- **API-Endpoint Tests** - Funktionalität aller APIs  
- **Hardware-Module Tests** - Kamera, Arm, Motoren, Sensoren
- **Stress Tests** - Performance unter Last
- **Error Handling** - Robustheit bei Fehlern

## 🚀 Schnell-Test (Shell Script)

### Installation:
```bash
chmod +x test.sh
```

### Ausführung:
```bash
# Standard (localhost:5000)
./test.sh

# Anderer Server
./test.sh http://192.168.251.1:5000
```

### Ausgabe:
```
🤖 Unkraut-2025 Test Script
==========================
📍 Teste Server: http://localhost:5000

🔍 Prüfe Server-Erreichbarkeit...
✅ Server erreichbar

🌐 Teste Web-Seiten...
Testing GET / ... ✅ OK (200)
Testing GET /control ... ✅ OK (200)
Testing GET /arm ... ✅ OK (200)
Testing GET /camera ... ✅ OK (200)
Testing GET /ai ... ✅ OK (200)

🔌 Teste API-Endpoints...
Testing GET /api/system/status ... ✅ OK (200)
...

📊 Test-Ergebnisse:
==================
Gesamt: 20 Tests
Erfolgreich: 20
Fehlgeschlagen: 0
Erfolgsrate: 100%

🎉 Alle Tests bestanden!
```

## 🐍 Erweiterte Tests (Python)

### Installation:
```bash
pip install requests
```

### Ausführung:

#### Alle Tests:
```bash
python test_unkraut2025.py
```

#### Schnelle Tests:
```bash
python test_unkraut2025.py --quick
```

#### Anderer Server:
```bash
python test_unkraut2025.py --url http://192.168.251.1:5000
```

#### Mit Report:
```bash
python test_unkraut2025.py --report my_test_report.json
```

### Ausgabe:
```
[14:23:15] INFO: 🚀 Starte Unkraut-2025 Test-Suite
[14:23:15] INFO: 📍 Teste Server: http://localhost:5000
[14:23:15] INFO: ✅ Server erreichbar
[14:23:15] INFO: 🌐 Teste Web-Seiten...
[14:23:15] INFO: ✅ GET / - 200 (0.045s)
[14:23:15] INFO:   📄 Dashboard: HTML-Seite geladen
[14:23:16] INFO: ✅ GET /control - 200 (0.032s)
[14:23:16] INFO:   📄 Fahrzeug-Steuerung: HTML-Seite geladen
...
[14:23:25] INFO: 📊 Test-Ergebnisse:
[14:23:25] INFO:   Gesamt: 47 Tests
[14:23:25] INFO:   Erfolgreich: 45 ✅
[14:23:25] INFO:   Fehlgeschlagen: 2 ❌
[14:23:25] INFO:   Erfolgsrate: 95.7%
[14:23:25] INFO:   Gesamtzeit: 9.84s
[14:23:25] INFO: 📄 Test-Bericht gespeichert: test_report.json
```

## 🔧 Hardware-Tests

### Getestete Module:
- **📷 Kamera:** OpenCV/Mock-Modus, Stream-Funktionalität
- **🦾 Roboterarm:** PCA9685/Mock, Servo-Steuerung, Presets
- **🚗 Motoren:** GPIO/Mock, Bewegungssteuerung
- **📊 Sensoren:** DS18B20/Mock, System-Statistiken
- **🧠 KI:** OpenCV/TensorFlow, Unkrauterkennung

### Hardware-Status:
```
[14:23:20] INFO: 🔧 Teste Hardware-Module...
[14:23:20] INFO:   📷 Kamera: mock - 640x480
[14:23:20] INFO:   🦾 Roboterarm: Mock - 6 Servos
[14:23:20] INFO:   🚗 Motoren: Mock
[14:23:20] INFO:   📊 Sensoren: Mock - Temp: 22.3°C
[14:23:20] INFO:   🧠 KI: OpenCV+Mock - 0 Erkennungen
```

## 📊 Test-Report (JSON)

Der Python-Tester erstellt einen detaillierten JSON-Report:

```json
{
  "timestamp": "2025-01-03T14:23:25.123456",
  "base_url": "http://localhost:5000",
  "total_tests": 47,
  "successful_tests": 45,
  "results": [
    {
      "endpoint": "/",
      "method": "GET",
      "status_code": 200,
      "expected": 200,
      "success": true,
      "response_time": 0.045,
      "content_length": 5234
    },
    ...
  ]
}
```

## 🚨 Fehlerdiagnose

### Häufige Probleme:

#### Server nicht erreichbar:
```bash
❌ Server nicht erreichbar: http://localhost:5000
💡 Starte den Server mit: python app/main.py
```

#### Template-Fehler:
```bash
❌ GET /arm - 500 (Jinja2 Template Error)
💡 Prüfe Template-Dateien in app/templates/
```

#### Hardware-Module fehlen:
```bash
❌ Hardware-Test fehlgeschlagen: No module named 'hardware.camera'
💡 Installiere Hardware-Module oder verwende Mock-Modus
```

#### API-Fehler:
```bash
❌ POST /api/arm/move/joint: Status 400
💡 Prüfe API-Parameter und Hardware-Verfügbarkeit
```

## 🎯 Test-Abdeckung

### Web-Interface (5 Tests):
- ✅ Dashboard `/`
- ✅ Fahrzeug-Steuerung `/control`  
- ✅ Roboterarm `/arm`
- ✅ Kamera `/camera`
- ✅ KI-Dashboard `/ai`

### API-Endpoints (25 Tests):
- ✅ System-Status
- ✅ Kamera-Steuerung & Stream
- ✅ Fahrzeug-Bewegung & Status
- ✅ Roboterarm-Steuerung & Presets
- ✅ KI-Unkrauterkennung

### Hardware-Module (6 Tests):
- ✅ Kamera-Manager
- ✅ Roboterarm-Controller
- ✅ Motor-Controller
- ✅ Sensor-Manager
- ✅ KI-Weed-Detector

### Stress & Error Tests (11 Tests):
- ✅ Parallele Anfragen
- ✅ Ungültige Endpoints
- ✅ Falsche Parameter
- ✅ Timeout-Verhalten

## 🔄 Kontinuierliche Tests

### Automatische Tests bei Änderungen:
```bash
# Watch-Modus (benötigt 'entr')
find . -name "*.py" | entr -r python test_unkraut2025.py --quick
```

### Cron-Job für regelmäßige Tests:
```bash
# Alle 30 Minuten testen
*/30 * * * * cd /home/pi/unkraut-2025 && python test_unkraut2025.py --report /tmp/test_$(date +\%H\%M).json
```

## 📈 Performance-Metriken

### Benchmarks:
- **Web-Seiten:** < 100ms Antwortzeit
- **API-Calls:** < 50ms Antwortzeit
- **Kamera-Stream:** < 33ms pro Frame
- **Hardware-Commands:** < 10ms Latenz

### Stress-Test Ziele:
- **Parallel Requests:** 10+ gleichzeitige Anfragen
- **Continuous Load:** 100+ Requests/Minute
- **Memory Usage:** < 512MB RAM
- **CPU Usage:** < 50% bei Normalbetrieb

---

**🎉 Mit dieser Test-Suite stellst du sicher, dass dein Unkraut-2025 System robust und zuverlässig funktioniert!**