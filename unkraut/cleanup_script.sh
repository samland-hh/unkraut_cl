#!/bin/bash
# unkraut/cleanup_project.sh
# Bereinigt überflüssige Dateien im Unkraut-2025 Projekt

# Farben für Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧹 Unkraut-2025 Projekt bereinigen${NC}"
echo "=================================="

# Projekt-Root ermitteln
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Prüfe ob wir bereits im Projekt-Root sind
if [ -f "run.py" ]; then
    PROJECT_ROOT="$(pwd)"
    echo -e "${GREEN}✅ Projekt-Root gefunden: $PROJECT_ROOT${NC}"
elif [ -f "$SCRIPT_DIR/run.py" ]; then
    PROJECT_ROOT="$SCRIPT_DIR"
    echo -e "${GREEN}✅ Projekt-Root gefunden: $PROJECT_ROOT${NC}"
else
    echo -e "${RED}❌ Fehler: Projekt-Root nicht gefunden!${NC}"
    echo "Script muss im Unkraut-Projekt ausgeführt werden."
    echo "Suche nach run.py in:"
    echo "  - Aktuelles Verzeichnis: $(pwd)"
    echo "  - Script-Verzeichnis: $SCRIPT_DIR"
    exit 1
fi

cd "$PROJECT_ROOT"

# Backup erstellen
echo -e "${YELLOW}📦 Erstelle Backup vor Cleanup...${NC}"
BACKUP_NAME="unkraut_backup_$(date +%Y%m%d_%H%M%S).tar.gz"
tar -czf "$BACKUP_NAME" . --exclude='.git' --exclude='*.tar.gz' --exclude='__pycache__'
echo -e "${GREEN}✅ Backup erstellt: $BACKUP_NAME${NC}"

# Größe vor Cleanup
SIZE_BEFORE=$(du -sh . | cut -f1)
echo -e "${BLUE}📊 Projektgröße vor Cleanup: $SIZE_BEFORE${NC}"

# Dateien zählen
FILES_BEFORE=$(find . -type f | wc -l)
echo -e "${BLUE}📁 Dateien vor Cleanup: $FILES_BEFORE${NC}"

echo ""
echo -e "${YELLOW}🚀 Starte Cleanup...${NC}"

# Zähler
DELETED_COUNT=0

# Funktion zum sicheren Löschen
safe_delete() {
    local file="$1"
    local reason="$2"
    
    if [ -f "$file" ]; then
        rm -f "$file"
        echo -e "${GREEN}✅ Gelöscht: $file${NC} ($reason)"
        ((DELETED_COUNT++))
    else
        echo -e "${YELLOW}⚠️  Nicht gefunden: $file${NC}"
    fi
}

# 1. BACKUP-DATEIEN (100% sicher)
echo -e "${BLUE}📄 Lösche Backup-Dateien...${NC}"
safe_delete "app/main (Kopie).py" "Backup"
safe_delete "app/main.py.backup" "Backup"
safe_delete "app/templates/dashboard (Kopie).html" "Backup"
safe_delete "app/templates/dashboard_shutdown_button.html" "Backup"
safe_delete "app/static/js/dashboard (Kopie).js" "Backup"
safe_delete "app/static/js/clean_dashboard_js.js" "Backup"
safe_delete "app/static/js/camera_enhanced_backup.js" "Backup"
safe_delete "ai/weed_detection_backup.py" "Backup"

# 2. DEBUG-DATEIEN (100% sicher)
echo -e "${BLUE}🐛 Lösche Debug-Dateien...${NC}"
safe_delete "debug_run_script.py" "Debug"
safe_delete "debug_script.py" "Debug"
safe_delete "quick_debug.py" "Debug"
safe_delete "test_function.py" "Debug"
safe_delete "test.py" "Debug"
safe_delete "arm_debug.py" "Debug"
safe_delete "gripper_debug_script.py" "Debug"

# 3. ARCHIV-DATEIEN (100% sicher)
echo -e "${BLUE}📦 Lösche Archiv-Dateien...${NC}"
safe_delete "app.tar" "Archiv"

# 4. SETUP-DUPLIKATE (Root-Versionen löschen)
echo -e "${BLUE}🔧 Bereinige Setup-Dateien...${NC}"
safe_delete "setup_complete.sh" "Duplikat"
safe_delete "setup_project_script.sh" "Duplikat"

# 5. MOBILE-TEST-TEMPLATES (nicht produktiv)
echo -e "${BLUE}📱 Lösche Mobile-Test-Templates...${NC}"
safe_delete "app/templates/mobile_test_alt.html" "Test-Template"
safe_delete "app/templates/mobile_test.html" "Test-Template"
safe_delete "app/templates/mobile_touch.html" "Test-Template"

# 6. MEHRFACH-CSS-DATEIEN (Vorsichtig - nur offensichtliche Duplikate)
echo -e "${BLUE}🎨 Bereinige CSS-Dateien...${NC}"
safe_delete "app/static/css/camera-enhanced.css" "Duplikat"
safe_delete "app/static/css/camera_enhanced.css" "Duplikat"
safe_delete "app/static/css/camera-gallery-fix.css" "Duplikat"

# 7. MEHRFACH-JAVASCRIPT-DATEIEN (Vorsichtig - nur offensichtliche Duplikate)
echo -e "${BLUE}📜 Bereinige JavaScript-Dateien...${NC}"
safe_delete "app/static/js/camera_base.js" "Duplikat"
safe_delete "app/static/js/camera_complete.js" "Duplikat"
safe_delete "app/static/js/camera_enhanced.js" "Duplikat"
safe_delete "app/static/js/camera-init.js" "Duplikat"
safe_delete "app/static/js/camera-tools.js" "Duplikat"
safe_delete "app/static/js/camera_tools.js" "Duplikat"

# 8. MEHRFACH-TEMPLATES (Vorsichtig - nur offensichtliche Duplikate)
echo -e "${BLUE}📄 Bereinige Template-Dateien...${NC}"
safe_delete "app/templates/camera_complete.html" "Duplikat"
safe_delete "app/templates/camera_debug.html" "Duplikat"
safe_delete "app/templates/camera_minimal.html" "Duplikat"

# 9. PYTHON-CACHE-DATEIEN (Sicher regenerierbar)
echo -e "${BLUE}🗑️ Lösche Python-Cache-Dateien...${NC}"
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true
CACHE_DELETED=$(find . -name "__pycache__" -type d | wc -l)
echo -e "${GREEN}✅ Python-Cache bereinigt ($CACHE_DELETED Verzeichnisse)${NC}"

# 10. LEERE VERZEICHNISSE
echo -e "${BLUE}📁 Prüfe leere Verzeichnisse...${NC}"
EMPTY_DIRS=$(find . -type d -empty -not -path "./.git/*" -not -path "./.*" | head -10)
if [ -n "$EMPTY_DIRS" ]; then
    echo -e "${YELLOW}⚠️  Leere Verzeichnisse gefunden:${NC}"
    echo "$EMPTY_DIRS"
else
    echo -e "${GREEN}✅ Keine leeren Verzeichnisse gefunden${NC}"
fi

echo ""
echo -e "${BLUE}📊 Cleanup-Statistik:${NC}"
echo "===================="

# Größe nach Cleanup
SIZE_AFTER=$(du -sh . | cut -f1)
FILES_AFTER=$(find . -type f | wc -l)
FILES_DELETED=$((FILES_BEFORE - FILES_AFTER))

echo -e "${GREEN}✅ Gelöschte Dateien: $DELETED_COUNT${NC}"
echo -e "${GREEN}✅ Projektgröße vorher: $SIZE_BEFORE${NC}"
echo -e "${GREEN}✅ Projektgröße nachher: $SIZE_AFTER${NC}"
echo -e "${GREEN}✅ Dateien vorher: $FILES_BEFORE${NC}"
echo -e "${GREEN}✅ Dateien nachher: $FILES_AFTER${NC}"
echo -e "${GREEN}✅ Backup erstellt: $BACKUP_NAME${NC}"

echo ""
echo -e "${YELLOW}🧪 Empfohlene Tests nach Cleanup:${NC}"
echo "1. python run.py  # App starten"
echo "2. Öffne: http://localhost:5000"
echo "3. Teste Dashboard, Kamera, Arm-Steuerung"
echo "4. Bei Problemen: tar -xzf $BACKUP_NAME"

echo ""
echo -e "${GREEN}🎉 Cleanup abgeschlossen!${NC}"

# Warnung für weitere Duplikate
echo ""
echo -e "${YELLOW}⚠️  Weitere mögliche Duplikate (manuell prüfen):${NC}"
echo "Routes-Duplikate:"
[ -f "app/routes/control.py" ] && [ -f "app/routes/control_routes.py" ] && echo "  • control.py vs control_routes.py"
[ -f "app/routes/debug_route.py" ] && [ -f "app/routes/debug_routes.py" ] && echo "  • debug_route.py vs debug_routes.py"
[ -f "app/routes/enhanced_camera_api.py" ] && [ -f "app/routes/camera_routes.py" ] && echo "  • enhanced_camera_api.py vs camera_routes.py"
[ -f "app/routes/roboter_arm_api.py" ] && [ -f "app/routes/arm_routes.py" ] && echo "  • roboter_arm_api.py vs arm_routes.py"

echo ""
echo -e "${BLUE}💡 Manuelle Prüfung:${NC}"
echo "diff app/routes/control.py app/routes/control_routes.py"
echo "diff app/routes/debug_route.py app/routes/debug_routes.py"
echo ""
echo -e "${GREEN}✅ Cleanup-Script abgeschlossen!${NC}"