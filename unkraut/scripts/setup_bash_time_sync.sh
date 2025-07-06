#!/bin/bash
# Setup Script für Bash Zeit-Synchronisation
# Unkraut-2025 Projekt

set -e

WORKDIR="$HOME/robo/claude/unkraut"
SCRIPT_DIR="$WORKDIR/scripts"
CONFIG_DIR="$SCRIPT_DIR/config"
LOG_DIR="$SCRIPT_DIR/logs"

echo "🕐 Setup Bash Zeit-Synchronisation für Unkraut-2025"
echo "================================================="

# Arbeitsverzeichnis wechseln
cd "$WORKDIR" || {
    echo "❌ Fehler: Kann nicht zu $WORKDIR wechseln"
    exit 1
}

# Verzeichnisse erstellen
echo "📁 Erstelle Verzeichnisstruktur..."
mkdir -p "$CONFIG_DIR"
mkdir -p "$LOG_DIR"

# Config-Datei erstellen
echo "⚙️  Erstelle Host-Konfiguration..."
cat > "$CONFIG_DIR/time_sync_hosts.conf" << 'EOF'
# Zeit-Synchronisation Host-Konfiguration
# Format: PRIORITÄT|HOST|USER|SSH_OPTIONS
# Priorität: niedrigere Zahlen = höhere Priorität

1|time.google.com|ubuntu|-o ConnectTimeout=5 -o StrictHostKeyChecking=no
2|pool.ntp.org|pi|-o ConnectTimeout=5 -o StrictHostKeyChecking=no
3|192.168.1.1|admin|-o ConnectTimeout=3 -o StrictHostKeyChecking=no
4|de.pool.ntp.org|user|-o ConnectTimeout=5 -o StrictHostKeyChecking=no
5|europe.pool.ntp.org|root|-o ConnectTimeout=5 -o StrictHostKeyChecking=no

# Lokale Zeitserver (Beispiele - anpassen nach Bedarf)
#6|192.168.1.100|pi|-o ConnectTimeout=3 -o StrictHostKeyChecking=no
#7|timeserver.local|admin|-o ConnectTimeout=3 -o StrictHostKeyChecking=no
EOF

# Zeit-Sync Script erstellen
echo "🔧 Erstelle Zeit-Synchronisation Script..."
cat > "$SCRIPT_DIR/time_sync.sh" << 'EOF'
#!/bin/bash
# Zeit-Synchronisation via SSH
# Unkraut-2025 Projekt

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
CONFIG_FILE="$SCRIPT_DIR/config/time_sync_hosts.conf"
LOG_FILE="$SCRIPT_DIR/logs/time_sync.log"

# Logging Funktion
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# SSH Zeit abrufen
get_remote_time() {
    local host="$1"
    local user="$2"
    local ssh_opts="$3"
    
    # Versuche Zeit via SSH zu holen
    ssh $ssh_opts "$user@$host" "date '+%Y-%m-%d %H:%M:%S'" 2>/dev/null
}

# Zeit setzen
set_system_time() {
    local remote_time="$1"
    local host="$2"
    
    if command -v timedatectl >/dev/null 2>&1; then
        # Systemd-basierte Systeme
        if timedatectl set-time "$remote_time" 2>/dev/null; then
            log "✅ Zeit erfolgreich gesetzt von $host: $remote_time"
            return 0
        fi
    fi
    
    # Fallback: date command
    if date -s "$remote_time" >/dev/null 2>&1; then
        log "✅ Zeit erfolgreich gesetzt von $host: $remote_time (via date)"
        return 0
    fi
    
    return 1
}

# Haupt-Synchronisation
sync_time() {
    log "🕐 Starte Zeit-Synchronisation..."
    
    # Prüfe ob Config-Datei existiert
    if [[ ! -f "$CONFIG_FILE" ]]; then
        log "❌ Config-Datei nicht gefunden: $CONFIG_FILE"
        return 1
    fi
    
    # Aktuelle Zeit loggen
    log "⏰ Aktuelle Zeit: $(date '+%Y-%m-%d %H:%M:%S')"
    
    # Hosts nach Priorität sortiert durchgehen
    while IFS='|' read -r priority host user ssh_opts || [[ -n "$priority" ]]; do
        # Kommentare und leere Zeilen überspringen
        [[ "$priority" =~ ^[[:space:]]*# ]] && continue
        [[ -z "$priority" ]] && continue
        
        log "🔍 Teste Host: $host (Priorität: $priority)"
        
        # Zeit vom Host abrufen
        remote_time=$(get_remote_time "$host" "$user" "$ssh_opts")
        
        if [[ -n "$remote_time" ]]; then
            log "📡 Zeit empfangen von $host: $remote_time"
            
            # Zeit setzen
            if set_system_time "$remote_time" "$host"; then
                log "🎉 Zeit-Synchronisation erfolgreich abgeschlossen"
                return 0
            else
                log "⚠️  Konnte Zeit nicht setzen (keine sudo-Rechte?)"
            fi
        else
            log "❌ Keine Verbindung zu $host möglich"
        fi
        
    done < <(sort -t'|' -k1,1n "$CONFIG_FILE")
    
    log "❌ Keine verfügbare Zeit-Quelle gefunden"
    return 1
}

# Script ausführen
main() {
    # Log-Verzeichnis erstellen falls nicht vorhanden
    mkdir -p "$(dirname "$LOG_FILE")"
    
    # Synchronisation starten
    sync_time
}

# Nur ausführen wenn Script direkt aufgerufen wird
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
EOF

# Berechtigungen setzen
echo "🔐 Setze Berechtigungen..."
chmod +x "$SCRIPT_DIR/time_sync.sh"
chmod 644 "$CONFIG_DIR/time_sync_hosts.conf"

# Cron-Job installieren
echo "⏰ Installiere Cron-Job..."
CRON_JOB="@reboot sleep 180 && sudo $SCRIPT_DIR/time_sync.sh"

# Prüfe ob Cron-Job bereits existiert
if ! crontab -l 2>/dev/null | grep -q "time_sync.sh"; then
    # Bestehende Crontab holen und neue Zeile hinzufügen
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    echo "✅ Cron-Job installiert: Startet 3 Minuten nach Boot (mit sudo)"
else
    echo "ℹ️  Cron-Job bereits vorhanden"
fi

# Sudo-Rechte für Zeit-Synchronisation einrichten
echo "🔐 Konfiguriere sudo-Rechte..."
SUDO_RULE="$USER ALL=(ALL) NOPASSWD: $SCRIPT_DIR/time_sync.sh, /usr/bin/timedatectl, /bin/date"

if ! sudo grep -q "time_sync.sh" /etc/sudoers.d/* 2>/dev/null; then
    echo "$SUDO_RULE" | sudo tee /etc/sudoers.d/time_sync >/dev/null
    sudo chmod 440 /etc/sudoers.d/time_sync
    echo "✅ Sudo-Rechte konfiguriert"
else
    echo "ℹ️  Sudo-Rechte bereits vorhanden"
fi

# Erste Log-Datei erstellen
echo "📝 Initialisiere Log-Datei..."
echo "$(date '+%Y-%m-%d %H:%M:%S') - Zeit-Synchronisation Setup abgeschlossen" > "$LOG_DIR/time_sync.log"

echo ""
echo "🎉 Setup erfolgreich abgeschlossen!"
echo ""
echo "📁 Installierte Dateien:"
echo "   - Script: $SCRIPT_DIR/time_sync.sh"
echo "   - Config: $CONFIG_DIR/time_sync_hosts.conf"
echo "   - Logs:   $LOG_DIR/time_sync.log"
echo ""
echo "⚡ Nächste Schritte:"
echo "   1. Config anpassen: nano $CONFIG_DIR/time_sync_hosts.conf"
echo "   2. Manuell testen:   $SCRIPT_DIR/time_sync.sh"
echo "   3. Bei Reboot läuft automatisch nach 3 Minuten"
echo ""
echo "📊 Status prüfen:"
echo "   tail -f $LOG_DIR/time_sync.log"
