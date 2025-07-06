# app/routes/debug_routes.py
"""
Debug-Routes für Mobile und Netzwerk-Probleme
"""
from flask import Blueprint, render_template, jsonify, request
import socket
import platform
import psutil
import os

bp = Blueprint('debug', __name__)

@bp.route('/mobile-test')
def mobile_test():
    """Mobile Navigation Test Seite"""
    return """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mobile Test - Unkraut-2025</title>
    <style>
        body { margin: 0; padding: 10px; font-family: Arial, sans-serif; 
               background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); 
               color: white; min-height: 100vh; }
        
        .test-header { background: rgba(0,0,0,0.8); padding: 15px; border-radius: 8px; 
                      margin-bottom: 20px; display: flex; justify-content: space-between; 
                      align-items: center; box-shadow: 0 4px 10px rgba(0,0,0,0.3); }
        
        .test-header h1 { margin: 0; font-size: 1.3rem; }
        
        .hamburger-btn { background: #28a745; color: white; border: none; 
                        padding: 12px 18px; border-radius: 8px; font-size: 20px; 
                        cursor: pointer; min-width: 60px; height: 50px; 
                        font-weight: bold; box-shadow: 0 2px 5px rgba(0,0,0,0.3); }
        
        .hamburger-btn:active { background: #218838; transform: scale(0.95); }
        
        .test-nav { display: none; flex-direction: column; gap: 12px; margin-top: 15px; 
                   background: rgba(0,0,0,0.95); padding: 20px; border-radius: 10px; 
                   box-shadow: 0 6px 20px rgba(0,0,0,0.5); }
        
        .test-nav.open { display: flex; }
        
        .test-nav a { background: #007bff; color: white; text-decoration: none; 
                     padding: 18px; border-radius: 8px; text-align: center; 
                     font-size: 16px; font-weight: bold; 
                     border: 2px solid rgba(255,255,255,0.2); 
                     min-height: 60px; display: flex; align-items: center; 
                     justify-content: center; }
        
        .test-nav a:active { background: #0056b3; transform: scale(0.98); }
        
        .test-info { background: rgba(255,255,255,0.1); padding: 20px; 
                    border-radius: 10px; margin: 20px 0; }
        
        .test-button { background: #ffc107; color: black; border: none; 
                      padding: 15px 20px; border-radius: 8px; font-size: 16px; 
                      margin: 8px 4px; cursor: pointer; min-height: 55px; 
                      font-weight: bold; }
        
        .test-button:active { background: #e0a800; transform: scale(0.95); }
        
        .debug-output { background: #000; color: #0f0; padding: 15px; 
                       border-radius: 8px; font-family: monospace; font-size: 13px; 
                       white-space: pre-wrap; max-height: 300px; overflow-y: auto; 
                       margin: 20px 0; border: 1px solid #333; }
        
        .button-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
        
        @media (max-width: 480px) {
            .button-grid { grid-template-columns: 1fr; }
            .test-header { padding: 10px; }
            .test-header h1 { font-size: 1.1rem; }
        }
    </style>
</head>
<body>
    <div class="test-header">
        <h1>📱 Mobile Navigation Test</h1>
        <button class="hamburger-btn" onclick="toggleTestNav()" id="hamburger">☰</button>
    </div>
    
    <nav class="test-nav" id="test-nav">
        <a href="/">🏠 Dashboard</a>
        <a href="/control">🎮 Fahrzeug</a>
        <a href="/arm">🦾 Roboterarm</a>
        <a href="/camera">📷 Kamera</a>
        <a href="/combined">🎯 Kamera+Arm</a>
        <a href="/ai">🧠 KI-Erkennung</a>
        <a href="/debug">🔧 Debug</a>
    </nav>
    
    <div class="test-info">
        <h3>📱 Navigation Test</h3>
        <p><strong>Status:</strong> <span id="nav-status">Bereit zum Testen</span></p>
        <p><strong>Bildschirm:</strong> <span id="screen-info"></span></p>
        <p><strong>Touch:</strong> <span id="touch-info"></span></p>
    </div>
    
    <div class="button-grid">
        <button class="test-button" onclick="testHamburger()">🍔 Hamburger Test</button>
        <button class="test-button" onclick="testTouch()">👆 Touch Test</button>
        <button class="test-button" onclick="testNavigation()">🧭 Navigation Test</button>
        <button class="test-button" onclick="clearLog()">🗑️ Log löschen</button>
    </div>
    
    <div class="debug-output" id="debug-output">🚀 Mobile Navigation Test gestartet...
Bildschirm: ${window.innerWidth}x${window.innerHeight}
Touch verfügbar: ${'ontouchstart' in window ? 'JA' : 'NEIN'}

Klicke auf das ☰ Symbol oben rechts um das Menü zu testen.
</div>

    <script>
        let testResults = [];
        
        function logTest(message) {
            const timestamp = new Date().toLocaleTimeString();
            const logMessage = `[${timestamp}] ${message}`;
            testResults.push(logMessage);
            updateLog();
            console.log(logMessage);
        }
        
        function updateLog() {
            document.getElementById('debug-output').textContent = testResults.join('\\n');
        }
        
        function clearLog() {
            testResults = [];
            logTest('Log gelöscht - Test neu gestartet');
        }
        
        function toggleTestNav() {
            const nav = document.getElementById('test-nav');
            const hamburger = document.getElementById('hamburger');
            const status = document.getElementById('nav-status');
            
            if (!nav || !hamburger) {
                logTest('❌ FEHLER: Navigation-Elemente nicht gefunden!');
                return;
            }
            
            nav.classList.toggle('open');
            const isOpen = nav.classList.contains('open');
            hamburger.textContent = isOpen ? '✕' : '☰';
            status.textContent = isOpen ? 'Menü GEÖFFNET' : 'Menü geschlossen';
            
            logTest(`✅ Navigation ${isOpen ? 'GEÖFFNET' : 'GESCHLOSSEN'}`);
        }
        
        function testHamburger() {
            logTest('=== HAMBURGER-MENÜ TEST START ===');
            
            const hamburger = document.getElementById('hamburger');
            const nav = document.getElementById('test-nav');
            
            if (!hamburger) {
                logTest('❌ Hamburger-Button NICHT GEFUNDEN');
                return;
            }
            
            if (!nav) {
                logTest('❌ Navigation NICHT GEFUNDEN');
                return;
            }
            
            // Element-Info
            const rect = hamburger.getBoundingClientRect();
            logTest(`✅ Hamburger gefunden: ${rect.width}x${rect.height} px`);
            logTest(`✅ Position: x=${Math.round(rect.x)}, y=${Math.round(rect.y)}`);
            logTest(`✅ Sichtbar: ${rect.width > 0 && rect.height > 0 ? 'JA' : 'NEIN'}`);
            
            // Automatischer Toggle-Test
            logTest('🔄 Teste automatisches Öffnen/Schließen...');
            toggleTestNav();
            setTimeout(() => {
                toggleTestNav();
                logTest('✅ Hamburger-Test ERFOLGREICH abgeschlossen');
            }, 1500);
        }
        
        function testTouch() {
            logTest('=== TOUCH TEST START ===');
            logTest(`ontouchstart: ${'ontouchstart' in window ? 'VERFÜGBAR' : 'NICHT VERFÜGBAR'}`);
            logTest(`maxTouchPoints: ${navigator.maxTouchPoints || 0}`);
            logTest(`Pointer Events: ${'onpointerdown' in window ? 'VERFÜGBAR' : 'NICHT VERFÜGBAR'}`);
            
            // Touch Event Test auf Hamburger
            const hamburger = document.getElementById('hamburger');
            if (hamburger) {
                hamburger.addEventListener('touchstart', function(e) {
                    logTest('✅ TOUCH START erkannt');
                }, { once: true });
                
                hamburger.addEventListener('touchend', function(e) {
                    logTest('✅ TOUCH END erkannt');
                }, { once: true });
                
                logTest('👆 Touch-Listener registriert. Berühre das ☰ Symbol.');
            }
        }
        
        function testNavigation() {
            logTest('=== NAVIGATION TEST START ===');
            
            const links = document.querySelectorAll('.test-nav a');
            logTest(`✅ ${links.length} Navigation-Links gefunden`);
            
            links.forEach((link, i) => {
                const text = link.textContent.trim();
                const href = link.getAttribute('href');
                logTest(`${i+1}. ${text} → ${href}`);
            });
            
            // Test ob Links erreichbar sind
            const testUrls = ['/', '/control', '/combined'];
            testUrls.forEach(url => {
                fetch(url, { method: 'HEAD' })
                    .then(response => {
                        logTest(`✅ ${url}: Status ${response.status}`);
                    })
                    .catch(error => {
                        logTest(`❌ ${url}: FEHLER - ${error.message}`);
                    });
            });
        }
        
        // Initialisierung
        document.addEventListener('DOMContentLoaded', function() {
            // Info anzeigen
            document.getElementById('screen-info').textContent = 
                `${window.innerWidth}x${window.innerHeight}`;
            document.getElementById('touch-info').textContent = 
                'ontouchstart' in window ? 'Verfügbar' : 'Nicht verfügbar';
            
            logTest('📱 Mobile Test-Seite geladen');
            logTest(`📐 Viewport: ${window.innerWidth}x${window.innerHeight}`);
            logTest(`🖥️ Screen: ${screen.width}x${screen.height}`);
            logTest(`📱 Mobile Layout: ${window.innerWidth <= 768 ? 'JA' : 'NEIN'}`);
            
            // Automatischer Test für sehr kleine Bildschirme
            if (window.innerWidth <= 480) {
                setTimeout(() => {
                    logTest('🤖 Auto-Test für kleinen Bildschirm...');
                    testHamburger();
                }, 2000);
            }
        });
    </script>
</body>
</html>"""

@bp.route('/debug')
def debug_info():
    """Debug-Informationen anzeigen"""
    try:
        return render_template('debug.html')
    except:
        # Fallback wenn Template fehlt
        return """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Debug - Unkraut-2025</title>
    <style>
        body { margin: 0; padding: 20px; font-family: Arial, sans-serif; 
               background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); 
               color: white; min-height: 100vh; }
        .card { background: rgba(255,255,255,0.1); padding: 20px; margin: 10px 0; 
                border-radius: 15px; backdrop-filter: blur(10px); }
        .btn { padding: 15px 20px; margin: 5px; border: none; border-radius: 8px; 
               cursor: pointer; font-weight: bold; font-size: 16px; min-height: 50px; }
        .btn-primary { background: #007bff; color: white; }
        .btn-success { background: #28a745; color: white; }
        .btn-warning { background: #ffc107; color: black; }
        .btn-danger { background: #dc3545; color: white; }
        .status-display { font-family: 'Courier New', monospace; background: rgba(0,0,0,0.3); 
                         padding: 15px; border-radius: 8px; white-space: pre-line; margin: 10px 0; }
        .debug-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; }
        @media (max-width: 768px) {
            .debug-grid { grid-template-columns: 1fr; }
            .btn { width: 100%; margin: 5px 0; }
        }
    </style>
</head>
<body>
    <div class="card">
        <h2>🔧 Debug - Mobile Navigation</h2>
        <p>Diagnose-Tools für Mobile-Probleme</p>
        
        <div class="debug-grid">
            <button class="btn btn-primary" onclick="testNavigation()">🧭 Navigation testen</button>
            <button class="btn btn-success" onclick="testAPI()">📡 API testen</button>
            <button class="btn btn-warning" onclick="showInfo()">📱 Geräte-Info</button>
            <button class="btn btn-danger" onclick="goToMobileTest()">📱 Mobile Test</button>
        </div>
    </div>

    <div class="card">
        <h3>🔗 Direkte Links</h3>
        <div class="debug-grid">
            <button class="btn btn-primary" onclick="goto('/')">🏠 Dashboard</button>
            <button class="btn btn-success" onclick="goto('/control')">🎮 Fahrzeug</button>
            <button class="btn btn-warning" onclick="goto('/arm')">🦾 Roboterarm</button>
            <button class="btn btn-primary" onclick="goto('/camera')">📷 Kamera</button>
            <button class="btn btn-danger" onclick="goto('/combined')">🎯 Kamera+Arm</button>
            <button class="btn btn-secondary" onclick="goto('/ai')">🧠 KI</button>
        </div>
    </div>

    <div class="card">
        <h3>📊 Debug-Ausgabe</h3>
        <div id="debug-output" class="status-display">Klicke auf einen Test-Button...</div>
    </div>

    <script>
        function log(msg) {
            const output = document.getElementById('debug-output');
            const time = new Date().toLocaleTimeString();
            output.textContent += `[${time}] ${msg}\\n`;
        }

        function testNavigation() {
            log('=== Navigation Test ===');
            const pages = ['/', '/control', '/arm', '/camera', '/combined', '/ai'];
            pages.forEach(page => {
                fetch(page, {method: 'HEAD'})
                    .then(r => log(`${page}: ${r.status} ${r.statusText}`))
                    .catch(e => log(`${page}: FEHLER - ${e.message}`));
            });
        }

        function testAPI() {
            log('=== API Test ===');
            fetch('/api/system/status')
                .then(r => r.json())
                .then(data => log('System Status API: OK'))
                .catch(e => log('System Status API: FEHLER - ' + e.message));
        }

        function showInfo() {
            log('=== Geräte-Info ===');
            log(`Bildschirm: ${window.innerWidth}x${window.innerHeight}`);
            log(`Touch: ${'ontouchstart' in window ? 'Ja' : 'Nein'}`);
            log(`User Agent: ${navigator.userAgent.substring(0, 50)}...`);
            log(`Platform: ${navigator.platform}`);
        }

        function goToMobileTest() {
            window.location.href = '/mobile-test';
        }

        function goto(path) {
            log(`Navigiere zu: ${path}`);
            window.location.href = path;
        }

        // Auto-Start Info
        setTimeout(showInfo, 1000);
    </script>
</body>
</html>"""

@bp.route('/api/debug/network')
def debug_network():
    """Netzwerk-Debug-Informationen"""
    try:
        # Server-IP-Adressen ermitteln
        hostname = socket.gethostname()
        ip_addresses = []
        
        # Alle Netzwerk-Interfaces
        for interface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    ip_addresses.append({
                        'interface': interface,
                        'ip': addr.address,
                        'netmask': addr.netmask
                    })
        
        # Client-Informationen
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR'))
        user_agent = request.headers.get('User-Agent', 'Unknown')
        
        # Server-Informationen
        server_info = {
            'hostname': hostname,
            'platform': platform.system(),
            'python_version': platform.python_version(),
            'server_port': request.environ.get('SERVER_PORT'),
            'server_name': request.environ.get('SERVER_NAME')
        }
        
        return jsonify({
            'server': server_info,
            'ip_addresses': ip_addresses,
            'client': {
                'ip': client_ip,
                'user_agent': user_agent,
                'host': request.host,
                'url': request.url,
                'method': request.method
            },
            'headers': dict(request.headers)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/api/debug/routes')
def debug_routes():
    """Alle verfügbaren Routes anzeigen"""
    try:
        from flask import current_app
        
        routes = []
        for rule in current_app.url_map.iter_rules():
            routes.append({
                'endpoint': rule.endpoint,
                'methods': list(rule.methods),
                'rule': rule.rule
            })
        
        return jsonify({'routes': routes})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500