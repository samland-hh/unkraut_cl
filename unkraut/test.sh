#!/bin/bash
# test.sh - Einfaches Test-Script für Unkraut-2025

echo "🤖 Unkraut-2025 Test Script"
echo "=========================="

# Farben für Output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Server URL
URL=${1:-"http://localhost:5000"}
echo "📍 Teste Server: $URL"
echo ""

# Funktion für HTTP-Tests
test_endpoint() {
    local method=$1
    local endpoint=$2
    local data=$3
    local expected=${4:-200}
    
    echo -n "Testing $method $endpoint ... "
    
    if [ "$method" == "GET" ]; then
        status=$(curl -s -o /dev/null -w "%{http_code}" "$URL$endpoint")
    elif [ "$method" == "POST" ]; then
        if [ -n "$data" ]; then
            status=$(curl -s -o /dev/null -w "%{http_code}" -X POST -H "Content-Type: application/json" -d "$data" "$URL$endpoint")
        else
            status=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$URL$endpoint")
        fi
    fi
    
    if [ "$status" == "$expected" ]; then
        echo -e "${GREEN}✅ OK ($status)${NC}"
        return 0
    else
        echo -e "${RED}❌ FAIL ($status, expected $expected)${NC}"
        return 1
    fi
}

# Prüfe ob Server läuft
echo "🔍 Prüfe Server-Erreichbarkeit..."
if ! curl -s "$URL" > /dev/null; then
    echo -e "${RED}❌ Server nicht erreichbar: $URL${NC}"
    echo "💡 Starte den Server mit: python app/main.py"
    exit 1
fi
echo -e "${GREEN}✅ Server erreichbar${NC}"
echo ""

# Test-Zähler
total=0
passed=0

# Web-Seiten testen
echo "🌐 Teste Web-Seiten..."
test_endpoint "GET" "/" && ((passed++))
test_endpoint "GET" "/control" && ((passed++))
test_endpoint "GET" "/arm" && ((passed++))
test_endpoint "GET" "/camera" && ((passed++))
test_endpoint "GET" "/ai" && ((passed++))
total=$((total + 5))
echo ""

# API-Endpoints testen
echo "🔌 Teste API-Endpoints..."
test_endpoint "GET" "/api/system/status" && ((passed++))
test_endpoint "POST" "/api/camera/capture" && ((passed++))
test_endpoint "POST" "/api/control/stop" && ((passed++))
test_endpoint "GET" "/api/control/status" && ((passed++))
test_endpoint "GET" "/api/arm/info" && ((passed++))
test_endpoint "POST" "/api/arm/emergency_stop" && ((passed++))
test_endpoint "POST" "/api/ai/detect" && ((passed++))
total=$((total + 7))
echo ""

# Fahrzeug-Steuerung testen
echo "🚗 Teste Fahrzeug-Steuerung..."
test_endpoint "POST" "/api/control/move" '{"direction":"forward","speed":50,"duration":0.1}' && ((passed++))
test_endpoint "POST" "/api/control/move" '{"direction":"left","speed":30,"duration":0.1}' && ((passed++))
test_endpoint "POST" "/api/control/move" '{"direction":"stop"}' && ((passed++))
total=$((total + 3))
echo ""

# Roboterarm testen
echo "🦾 Teste Roboterarm..."
test_endpoint "POST" "/api/arm/move/joint" '{"joint":"base","angle":90}' && ((passed++))
test_endpoint "POST" "/api/arm/move/preset" '{"preset":"home","duration":2.0}' && ((passed++))
test_endpoint "POST" "/api/arm/tool/activate" '{"duration":3.0}' && ((passed++))
total=$((total + 3))
echo ""

# Fehlerbehandlung testen
echo "⚠️ Teste Fehlerbehandlung..."
test_endpoint "GET" "/nonexistent" "" 404 && ((passed++))
test_endpoint "POST" "/api/invalid" "" 404 && ((passed++))
total=$((total + 2))
echo ""

# Kamera-Stream testen
echo "📹 Teste Kamera-Stream..."
stream_status=$(curl -s -o /dev/null -w "%{http_code}" "$URL/api/camera/stream" --max-time 3)
if [ "$stream_status" == "200" ]; then
    echo -e "${GREEN}✅ Kamera-Stream verfügbar${NC}"
    ((passed++))
else
    echo -e "${RED}❌ Kamera-Stream nicht verfügbar ($stream_status)${NC}"
fi
total=$((total + 1))
echo ""

# Ergebnisse
echo "📊 Test-Ergebnisse:"
echo "=================="
success_rate=$((passed * 100 / total))

if [ $success_rate -eq 100 ]; then
    color=$GREEN
elif [ $success_rate -ge 80 ]; then
    color=$YELLOW
else
    color=$RED
fi

echo -e "Gesamt: $total Tests"
echo -e "Erfolgreich: ${GREEN}$passed${NC}"
echo -e "Fehlgeschlagen: ${RED}$((total - passed))${NC}"
echo -e "Erfolgsrate: ${color}${success_rate}%${NC}"

if [ $passed -eq $total ]; then
    echo -e "\n${GREEN}🎉 Alle Tests bestanden!${NC}"
    exit 0
else
    echo -e "\n${RED}❌ Einige Tests fehlgeschlagen.${NC}"
    echo -e "${YELLOW}💡 Prüfe die Logs für Details.${NC}"
    exit 1
fi