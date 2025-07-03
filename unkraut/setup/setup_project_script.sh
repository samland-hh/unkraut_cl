#!/bin/bash

# Unkraut-2025 Projekt Setup Script
echo "Creating Unkraut-2025 project structure..."

# Hauptverzeichnisse erstellen
mkdir -p app/{routes,templates,static/{css,js,images},utils}
mkdir -p hardware
mkdir -p ai/{models,training_data}
mkdir -p config
mkdir -p scripts
mkdir -p logs
mkdir -p backups/{images,configs,data}
mkdir -p data/{images,videos,maps,sessions}
mkdir -p docs/images
mkdir -p tests
mkdir -p deployment/{docker,ansible,systemd}
mkdir -p .github/{workflows,ISSUE_TEMPLATE}

# Python __init__.py Dateien erstellen
touch app/__init__.py
touch app/routes/__init__.py
touch app/utils/__init__.py
touch hardware/__init__.py
touch ai/__init__.py
touch tests/__init__.py

# Hauptdateien erstellen
cat > run.py << 'EOF'
#!/usr/bin/env python3
"""
Unkraut-2025 Main Entry Point
"""
from app.main import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
EOF

cat > requirements.txt << 'EOF'
Flask==2.3.3
gunicorn==21.2.0
opencv-python==4.8.1.78
numpy==1.24.3
RPi.GPIO==0.7.1
picamera2==0.3.12
requests==2.31.0
python-dotenv==1.0.0
EOF

cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
env.bak/
venv.bak/

# Logs
*.log
logs/

# Config files with secrets
config/secrets.json
.env

# Data files
data/images/
data/videos/
data/sessions/
backups/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Hardware specific
*.bin
*.img
EOF

cat > README.md << 'EOF'
# 🤖 Unkraut-2025 - Autonomer Unkraut-Roboter

Autonomer Unkraut-Roboter mit Raspberry Pi für die automatisierte oder manuell gesteuerte Bekämpfung von Unkraut.

## Features

- 📷 Kamerastreaming über mjpg-streamer
- 🌐 Webbasierte Steuerung per Tablet/Handy/PC
- 🛜 WLAN Access Point Modus (offline-autark)
- 🔧 Erweiterbar mit Motorsteuerung, AI-Vision, GPS
- 📦 Backup- und Wiederherstellungssystem

## Installation

```bash
# Repository klonen
git clone https://github.com/samland-hh/unkraut.git
cd unkraut

# Dependencies installieren
pip install -r requirements.txt

# Anwendung starten
python run.py
```

## Hardware

- Raspberry Pi 4
- Pi Camera
- Motoren/Servos
- Sensoren

## Lizenz

MIT License
EOF

cat > .env.example << 'EOF'
# Unkraut-2025 Environment Variables
FLASK_ENV=development
FLASK_DEBUG=True
CAMERA_RESOLUTION=640x480
CAMERA_FRAMERATE=30
WIFI_AP_SSID=Unkraut-2025
WIFI_AP_PASSWORD=unkraut123
EOF

# GitHub Workflow erstellen
cat > .github/workflows/ci.yml << 'EOF'
name: CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        
    - name: Run tests
      run: |
        python -m pytest tests/
EOF

# Basic Flask App erstellen
cat > app/main.py << 'EOF'
from flask import Flask, render_template, jsonify
from .routes import camera, control, system

def create_app():
    app = Flask(__name__)
    
    # Routes registrieren
    app.register_blueprint(camera.bp)
    app.register_blueprint(control.bp)
    app.register_blueprint(system.bp)
    
    @app.route('/')
    def index():
        return render_template('index.html')
    
    return app

app = create_app()
EOF

echo "✅ Projekt Struktur erstellt!"
echo "Nächste Schritte:"
echo "1. git add ."
echo "2. git commit -m 'Initial project structure'"
echo "3. git push origin main"