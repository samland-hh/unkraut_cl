#!/bin/bash
# Auto-Shutdown nach 8 Stunden für Batterie-Betrieb
# Unkraut-2025 Projekt

RUNTIME_HOURS=8
RUNTIME_SECONDS=$((RUNTIME_HOURS * 3600))
LOG_FILE="$HOME/robo/claude/unkraut/scripts/logs/auto_shutdown.log"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Log-Verzeichnis erstellen
mkdir -p "$(dirname "$LOG_FILE")"

log "🔋 Auto-Shutdown Timer gestartet - ${RUNTIME_HOURS}h Laufzeit"
log "📅 Boot-Zeit: $(uptime -s)"
log "⏰ Geplanter Shutdown: $(date -d "+${RUNTIME_HOURS} hours" '+%Y-%m-%d %H:%M:%S')"

# Warnung 30 Minuten vorher
WARNING_TIME=$((RUNTIME_SECONDS - 1800))
(
    sleep $WARNING_TIME
    log "⚠️  WARNUNG: Shutdown in 30 Minuten!"
    
    # Optional: LED blinken oder Piepton (falls Hardware vorhanden)
    # echo "Shutdown in 30min" | wall
    
    sleep 1800
    log "🔴 SHUTDOWN: Batterie-Schutz nach ${RUNTIME_HOURS}h Laufzeit"
    log "📊 Uptime: $(uptime -p)"
    
    # Graceful shutdown
    sudo shutdown -h now
) &

log "✅ Shutdown-Timer läuft im Hintergrund (PID: $!)"