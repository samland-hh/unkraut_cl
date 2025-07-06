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
        if sudo timedatectl set-time "$remote_time" 2>/dev/null; then
            log "✅ Zeit erfolgreich gesetzt von $host: $remote_time"
            return 0
        fi
    fi
    
    # Fallback: date command
    if sudo date -s "$remote_time" >/dev/null 2>&1; then
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
