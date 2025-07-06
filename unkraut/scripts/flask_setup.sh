#!/bin/bash
# Setup Flask Auto-Start für Unkraut-2025

WORKDIR="$HOME/robo/claude/unkraut"
SERVICE_NAME="flask-unkraut"
PYTHON_SCRIPT="run.py"
VENV_PATH="$WORKDIR/venv"

echo "🐍 Setup Flask Auto-Start mit Virtual Environment"
echo "================================================"

cd "$WORKDIR" || {
    echo "❌ Kann nicht zu $WORKDIR wechseln"
    exit 1
}

# Virtual Environment prüfen/erstellen
if [[ ! -d "$VENV_PATH" ]]; then
    echo "📦 Erstelle Virtual Environment..."
    python3 -m venv venv
    echo "✅ Virtual Environment erstellt"
fi

# venv aktivieren
source venv/bin/activate
echo "🔗 Virtual Environment aktiviert"

# Flask installieren falls nicht vorhanden
if ! python -c "import flask" 2>/dev/null; then
    echo "📦 Installiere Flask in venv..."
    pip install flask
    echo "✅ Flask installiert"
else
    echo "ℹ️  Flask bereits in venv vorhanden"
fi
if [[ ! -f "$PYTHON_SCRIPT" ]]; then
    echo "❌ Python-Script nicht gefunden: $PYTHON_SCRIPT"
    echo "📝 Erstelle Beispiel-Flask-App..."
    
    cat > "$PYTHON_SCRIPT" << 'EOF'
#!/usr/bin/env python3
from flask import Flask, jsonify
import datetime

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        'status': 'Unkraut Flask Server läuft!',
        'time': datetime.datetime.now().isoformat(),
        'uptime': 'Seit Boot gestartet'
    })

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
EOF
    
    chmod +x "$PYTHON_SCRIPT"
    echo "✅ Beispiel Flask-App erstellt"
fi

# Flask installieren falls nicht vorhanden
if ! python3 -c "import flask" 2>/dev/null; then
    echo "📦 Installiere Flask..."
    pip3 install flask
fi

# Systemd Service erstellen
echo "⚙️  Erstelle Systemd Service (startet nach 140 Sekunden)..."
sudo tee "/etc/systemd/system/${SERVICE_NAME}.service" > /dev/null << EOF
[Unit]
Description=Unkraut Flask Server
After=network.target
Wants=network.target

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory=$WORKDIR
Environment=PYTHONPATH=$WORKDIR
Environment=FLASK_ENV=production
Environment=PATH=$VENV_PATH/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
ExecStartPre=/bin/sleep 140
ExecStart=$VENV_PATH/bin/python $WORKDIR/$PYTHON_SCRIPT
Restart=always
RestartSec=10
TimeoutStartSec=180
StandardOutput=journal
StandardError=journal

# Graceful shutdown
KillMode=mixed
KillSignal=SIGTERM
TimeoutStopSec=30

[Install]
WantedBy=multi-user.target
EOF

# Service aktivieren
echo "🔧 Aktiviere Service..."
sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"

echo ""
echo "✅ Flask Auto-Start konfiguriert!"
echo ""
echo "🚀 Befehle:"
echo "   Start:   sudo systemctl start $SERVICE_NAME"
echo "   Stop:    sudo systemctl stop $SERVICE_NAME"
echo "   Status:  sudo systemctl status $SERVICE_NAME"
echo "   Logs:    sudo journalctl -u $SERVICE_NAME -f"
echo ""
echo "🌐 Server läuft auf: http://$(hostname -I | cut -d' ' -f1):5000"
echo ""
echo "🔄 Service startet automatisch bei Boot (nach 140s)!"
echo ""
echo "ℹ️  Service wird NICHT sofort gestartet (wegen 140s Delay)"
echo "   Bei Reboot startet Flask automatisch nach 140 Sekunden"
echo ""
echo "🧪 Zum sofortigen Testen (ohne Delay):"
echo "   cd $WORKDIR && source venv/bin/activate && python run.py"