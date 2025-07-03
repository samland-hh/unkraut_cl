#!/bin/bash
# Script zur Zeitübertragung von PC auf Pi per SSH
# Verwendung: ./sync_time_to_pi.sh [user@pi-ip]
set -e
echo "=== Zeit per SSH auf Pi übertragen ==="
echo ""
# Standard SSH-Config Hosts
PRIMARY_PI_HOST="unkraut-251"
FALLBACK_PI_HOST="unkrautl"
# Parameter prüfen
if [ $# -eq 1 ]; then
    PI_TARGET="$1"
else
    # Primären Host testen
    echo ">>> Teste Verbindung zu $PRIMARY_PI_HOST..."
    if ssh -o ConnectTimeout=5 -o BatchMode=yes "$PRIMARY_PI_HOST" "echo 'SSH OK'" 2>/dev/null; then
        PI_TARGET="$PRIMARY_PI_HOST"
        echo "✓ Verwende $PRIMARY_PI_HOST"
    else
        echo "⚠ $PRIMARY_PI_HOST nicht erreichbar, versuche $FALLBACK_PI_HOST..."
        if ssh -o ConnectTimeout=5 -o BatchMode=yes "$FALLBACK_PI_HOST" "echo 'SSH OK'" 2>/dev/null; then
            PI_TARGET="$FALLBACK_PI_HOST"
            echo "✓ Verwende $FALLBACK_PI_HOST"
        else
            echo "Fehler: Weder $PRIMARY_PI_HOST noch $FALLBACK_PI_HOST erreichbar"
            echo ""
            echo "Prüfe:"
            echo "- Sind die Pis erreichbar?"
            echo "- SSH-Config korrekt? (~/.ssh/config)"
            echo "- SSH-Key konfiguriert?"
            exit 1
        fi
    fi
fi
echo "Ziel-Pi: $PI_TARGET"
echo ""
# Aktuelle Zeit des PCs
PC_TIME=$(date '+%Y-%m-%d %H:%M:%S')
echo "PC-Zeit: $PC_TIME"
# SSH-Verbindung final testen (falls manuell angegeben)
if [ $# -eq 1 ]; then
    echo ">>> Teste SSH-Verbindung..."
    if ! ssh -o ConnectTimeout=5 -o BatchMode=yes "$PI_TARGET" "echo 'SSH OK'" 2>/dev/null; then
        echo "Fehler: SSH-Verbindung zu $PI_TARGET fehlgeschlagen"
        echo ""
        echo "Prüfe:"
        echo "- Ist der Pi erreichbar?"
        echo "- SSH-Config korrekt? (~/.ssh/config)"
        echo "- SSH-Key konfiguriert?"
        exit 1
    fi
fi
# Aktuelle Pi-Zeit anzeigen
echo ">>> Aktuelle Pi-Zeit:"
ssh "$PI_TARGET" "date"
echo ""
echo ">>> Übertrage Zeit auf Pi..."
# Zeit auf Pi setzen
ssh "$PI_TARGET" "sudo date -s '$PC_TIME'"
# Hardware-Clock versuchen zu setzen (kann auf Pi fehlschlagen)
echo ">>> Versuche Hardware-Clock zu synchronisieren..."
if ssh "$PI_TARGET" "sudo hwclock -w" 2>/dev/null; then
    echo "✓ Hardware-Clock aktualisiert"
else
    echo "⚠ Hardware-Clock Warnung: Zugriff fehlgeschlagen"
    echo "  (Systemzeit wurde trotzdem gesetzt)"
fi
echo ">>> Neue Pi-Zeit:"
ssh "$PI_TARGET" "date"
echo ""
echo "=== Zeit erfolgreich übertragen! ==="
echo ""
echo "PC-Zeit:  $PC_TIME"
echo "Pi-Zeit:  $(ssh "$PI_TARGET" "date '+%Y-%m-%d %H:%M:%S'")"
echo ""
# Zeitdifferenz berechnen
PC_EPOCH=$(date '+%s')
PI_EPOCH=$(ssh "$PI_TARGET" "date '+%s'")
DIFF=$((PC_EPOCH - PI_EPOCH))
if [ $DIFF -eq 0 ]; then
    echo "✓ Zeiten sind synchron"
elif [ ${DIFF#-} -le 2 ]; then
    echo "✓ Zeiten sind nahezu synchron (${DIFF}s Differenz)"
else
    echo "⚠ Warnung: ${DIFF}s Zeitdifferenz"
fi
echo ""
echo "Hardware-Clock wurde aktualisiert - Zeit bleibt nach Reboot erhalten."