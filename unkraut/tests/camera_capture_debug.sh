#!/bin/bash
# unkraut/debug_camera_capture.sh
# Debuggt was /api/camera/capture zurückgibt

echo "🔍 Debug Camera Capture API"
echo "=========================="

URL="http://localhost:5000"

echo "📡 Teste /api/camera/capture..."
echo "Response Headers:"
curl -s -i -X POST "$URL/api/camera/capture" | head -20

echo ""
echo "Raw Response Body:"
curl -s -X POST "$URL/api/camera/capture" | head -10

echo ""
echo "Response als hex dump:"
curl -s -X POST "$URL/api/camera/capture" | hexdump -C | head -10

echo ""
echo "Content-Type prüfen:"
curl -s -I -X POST "$URL/api/camera/capture" | grep -i content-type