# 🌱 Unkraut-2025 - Autonomes Raspberry Pi System

Vollständige Dokumentation für das batteriebetriebene, autonome Raspberry Pi System mit automatischer Zeit-Synchronisation, Flask-Server und 8-Stunden-Laufzeit.

## 🎯 System-Übersicht

Das System kombiniert mehrere Komponenten für einen vollautomatischen Betrieb:

- **🕐 Zeit-Synchronisation** via SSH (ohne NTP)
- **🐍 Flask Web-Server** mit Virtual Environment
- **🔋 Auto-Shutdown** nach 8 Stunden (Batterie-Schutz)
- **📊 Uptime-Monitoring** alle 5 Minuten
- **📡 Access Point** Modus (192.168.251.1)

## ⏰ Boot-Timeline

| Zeit | Aktion | Beschreibung |
|------|--------|--------------|
| **0s** | 🚀 System Boot | Raspberry Pi startet |
| **0s** | 📊 Uptime-Log | Boot-Script startet |
| **130s** | 🕐 Zeit-Sync | Zeit-Synchronisation via SSH |
| **140s** | 🐍 Flask Start | Web-Server startet |
| **8h** | 🔴 Shutdown | Automatisches Herunterfahren |

## 📁 Verzeichnisstruktur

```
/home/jan/
├── bin/
│   └── create_uptime_log.sh           # Uptime Boot-Script
└── robo/claude/unkraut/
    ├── venv/                          # Python Virtual Environment
    ├── run.py                         # Flask Haupt-Script
    └── scripts/
        ├── time_sync.sh               # Zeit-Synchronisation
        ├── auto_shutdown.sh           # 8h Auto-Shutdown
        ├── setup_bash_time_sync.sh    # Zeit-Sync Setup
        ├── setup_flask_autostart.sh   # Flask Setup
        ├── config/
        │   └── time_sync_hosts.conf   # Zeit-Server Konfiguration
        └── logs/
            ├── time_sync.log          # Zeit-Sync Logs
            └── auto_shutdown.log      # Shutdown Logs
```

## 🔧 Aktuelle Cron-Jobs

```bash
# Crontab Inhalt (crontab -l)
# m h  dom mon dow   command

# Boot-Script beim Systemstart
@reboot /home/jan/bin/create_uptime_log.sh

# Uptime alle 5 Minuten loggen
*/5 * * * * echo "$(date): $(uptime)" > /tmp/uptime

# Zeit synchronisieren nach 130 sec
@reboot sleep 130 && /home/jan/robo/claude/unkraut/scripts/time_sync.sh >/dev/null 2>&1

# Nach 8 std ist Schluss dann shutdown
@reboot /home/jan/robo/claude/unkraut/scripts/auto_shutdown.sh >/dev/null 2>&1
```

## 🐍 Flask Systemd Service

```ini
# /etc/systemd/system/flask-unkraut.service
[Unit]
Description=Unkraut Flask Server
After=network.target
Wants=network.target

[Service]
Type=simple
User=jan
Group=jan
WorkingDirectory=/home/jan/robo/claude/unkraut
Environment=PYTHONPATH=/home/jan/robo/claude/unkraut
Environment=FLASK_ENV=production
Environment=PATH=/home/jan/robo/claude/unkraut/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
ExecStartPre=/bin/sleep 140
ExecStart=/home/jan/robo/claude/unkraut/venv/bin/python /home/jan/robo/claude/unkraut/run.py
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
```

## 🕐 Zeit-Synchronisation Konfiguration

```bash
# scripts/config/time_sync_hosts.conf
# Format: PRIORITÄT|HOST|USER|SSH_OPTIONS

# VERBUNDENER CLIENT - HÖCHSTE PRIORITÄT  
1|192.168.251.70|jan|-o ConnectTimeout=3 -o StrictHostKeyChecking=no

# BACKUP ZEITSERVER
2|pool.ntp.org|ubuntu|-o ConnectTimeout=5 -o StrictHostKeyChecking=no
3|time.google.com|user|-o ConnectTimeout=5 -o StrictHostKeyChecking=no
4|de.pool.ntp.org|pi|-o ConnectTimeout=5 -o StrictHostKeyChecking=no
```

## 🚀 Installation & Setup

### Komplett-Setup:
```bash
cd $HOME/robo/claude/unkraut

# Zeit-Synchronisation installieren
chmod +x scripts/setup_bash_time_sync.sh
./scripts/setup_bash_time_sync.sh

# Flask Auto-Start installieren  
chmod +x scripts/setup_flask_autostart.sh
./scripts/setup_flask_autostart.sh

# Alle Scripts ausführbar machen
chmod +x scripts/*.sh

# Cron-Jobs sind bereits installiert
```

## 📊 System-Monitoring

### Service Status prüfen:
```bash
# Flask Service
sudo systemctl status flask-unkraut
sudo journalctl -u flask-unkraut -f

# Zeit-Sync Logs
tail -f scripts/logs/time_sync.log

# Auto-Shutdown Logs
tail -f scripts/logs/auto_shutdown.log

# Uptime Monitor
cat /tmp/uptime
```

### Netzwerk Status:
```bash
# Eigene IP anzeigen
ip a

# Verbundene Clients scannen
nmap -sn 192.168.251.0/24

# ARP-Tabelle
arp -a
```

## 🌐 Web-Zugriff

- **Flask Server:** http://192.168.251.1:5000
- **Cockpit (falls installiert):** https://192.168.251.1:9090

### Von verbundenem Client testen:
```bash
curl http://192.168.251.1:5000
curl http://192.168.251.1:5000/health
```

## 🔧 Wartung & Debugging

### Manuelle Tests:
```bash
# Zeit-Sync manuell ausführen
cd ~/robo/claude/unkraut
./scripts/time_sync.sh

# Flask manuell starten
source venv/bin/activate
python run.py

# Auto-Shutdown testen (VORSICHT!)
./scripts/auto_shutdown.sh
```

### Logs prüfen:
```bash
# Alle System-Logs
sudo journalctl -f

# Cron-Logs
sudo journalctl -u cron -f

# Boot-Messages
dmesg | tail -20
```

### Service-Verwaltung:
```bash
# Flask Service steuern
sudo systemctl start flask-unkraut
sudo systemctl stop flask-unkraut
sudo systemctl restart flask-unkraut
sudo systemctl disable flask-unkraut  # Boot-Start deaktivieren

# Service-Status
sudo systemctl status flask-unkraut --no-pager -l
```

## 🔋 Batterie-Management

### 8-Stunden Auto-Shutdown:
- **Warnung:** 30 Minuten vor Shutdown
- **Graceful Shutdown:** Alle Services werden sauber beendet
- **Log-Eintrag:** Shutdown-Grund wird protokolliert

### Laufzeit anpassen:
```bash
# auto_shutdown.sh editieren
nano scripts/auto_shutdown.sh

# RUNTIME_HOURS=8 auf gewünschte Stunden ändern
RUNTIME_HOURS=6  # Für 6 Stunden
```

## 📧 Mail-Benachrichtigungen

Cron-Mails sind deaktiviert (`>/dev/null 2>&1`), aber alle Aktivitäten werden in Logdateien protokolliert.

### Mails aktivieren (optional):
```bash
crontab -e
# >/dev/null 2>&1 entfernen für Mail-Benachrichtigungen
```

## 🚨 Troubleshooting

### Zeit-Sync funktioniert nicht:
```bash
# SSH-Verbindung testen
ssh -o ConnectTimeout=3 jan@192.168.251.70 "date"

# SSH-Key kopieren
ssh-copy-id jan@192.168.251.70

# Hosts in Netzwerk finden
nmap -sn 192.168.251.0/24
```

### Flask startet nicht:
```bash
# Virtual Environment prüfen
cd ~/robo/claude/unkraut
source venv/bin/activate
python run.py

# Service-Logs anzeigen
sudo journalctl -u flask-unkraut -n 50
```

### Shutdown funktioniert nicht:
```bash
# Script-Rechte prüfen
ls -la scripts/auto_shutdown.sh

# Sudo-Rechte testen
sudo shutdown -h +1  # Test-Shutdown in 1 Minute
sudo shutdown -c     # Abbrechen
```

## 🎯 Erweiterte Konfiguration

### Zusätzliche Zeit-Server:
```bash
echo "6|192.168.251.100|pi|-o ConnectTimeout=3" >> scripts/config/time_sync_hosts.conf
```

### Flask-Port ändern:
```bash
# run.py editieren
nano run.py
# app.run(host='0.0.0.0', port=8080)  # Anderer Port
```

### Monitoring erweitern:
```bash
# CPU-Temperatur loggen
echo "*/10 * * * * echo \"\$(date): \$(vcgencmd measure_temp)\" >> /tmp/temperature" | crontab -
```

## 📋 Checkliste nach Reboot

✅ **0-2 Min:** System hochgefahren  
✅ **2-3 Min:** Zeit-Sync erfolgreich  
✅ **3-4 Min:** Flask Server läuft  
✅ **Laufend:** Uptime wird alle 5 Min geloggt  
✅ **8h später:** Automatischer Shutdown  

### Status schnell prüfen:
```bash
# Alles in einem Befehl
echo "=== SYSTEM STATUS ===" && \
date && \
uptime && \
sudo systemctl is-active flask-unkraut && \
tail -1 scripts/logs/time_sync.log && \
curl -s http://localhost:5000 || echo "Flask nicht erreichbar"
```

---

## 🎉 Fazit

Das Unkraut-2025 System ist ein vollständig autonomes, batteriebetriebenes Raspberry Pi Setup mit:

- **Zuverlässiger Zeit-Synchronisation** ohne Internet-Abhängigkeit
- **Robustem Flask Web-Server** mit Auto-Restart
- **Intelligentem Batterie-Management** mit 8h Laufzeit
- **Professionellem Logging** aller Komponenten
- **Einfacher Wartung** über standardisierte Tools

**Ideal für:** IoT-Projekte, Feldstudien, temporäre Installationen, Prototyping

**Getestet auf:** Raspberry Pi mit Debian/Raspbian, Python 3.x, systemd