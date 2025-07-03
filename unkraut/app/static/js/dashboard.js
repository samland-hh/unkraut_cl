// app/static/js/dashboard.js - Dashboard JavaScript

function moveRobot(direction) {
    fetch('/api/control/move', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({direction: direction, speed: 50, duration: 1})
    })
    .then(r => r.json())
    .then(data => {
        console.log('Move:', data);
        showNotification(`🚗 Fahre ${direction}`, 'success');
    })
    .catch(err => {
        console.error('Move error:', err);
        showNotification('❌ Bewegung fehlgeschlagen', 'error');
    });
}

function stopAll() {
    Promise.all([
        fetch('/api/control/stop', {method: 'POST'}),
        fetch('/api/arm/emergency_stop', {method: 'POST'})
    ])
    .then(() => {
        showNotification('🚨 ALLES GESTOPPT', 'warning');
    })
    .catch(err => {
        console.error('Stop error:', err);
        showNotification('❌ Stopp fehlgeschlagen', 'error');
    });
}

function captureImage() {
    fetch('/api/camera/capture', {method: 'POST'})
    .then(r => r.json())
    .then(data => {
        if (data.filename) {
            showNotification('📸 Foto: ' + data.filename, 'success');
        } else {
            showNotification('❌ Foto-Fehler: ' + data.error, 'error');
        }
    })
    .catch(err => {
        console.error('Capture error:', err);
        showNotification('❌ Kamera-Fehler', 'error');
    });
}

function detectWeeds() {
    showNotification('🔄 Analysiere Kamerabild...', 'info');
    
    fetch('/api/ai/detect', {method: 'POST'})
    .then(r => r.json())
    .then(data => {
        if (data.detections) {
            const count = data.detections.length;
            const confidence = (data.confidence * 100).toFixed(1);
            showNotification(`🔍 ${count} Unkraut erkannt (${confidence}% Konfidenz)`, 'success');
        } else {
            showNotification('❌ Erkennung fehlgeschlagen: ' + data.error, 'error');
        }
    })
    .catch(err => {
        console.error('Detection error:', err);
        showNotification('❌ KI-Fehler', 'error');
    });
}

function armHome() {
    fetch('/api/arm/move/preset', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({preset: 'home'})
    })
    .then(r => r.json())
    .then(data => {
        if (data.status === 'success') {
            showNotification('🏠 Arm fährt Home', 'success');
        } else {
            showNotification('❌ Arm-Fehler: ' + data.error, 'error');
        }
    })
    .catch(err => {
        console.error('Arm error:', err);
        showNotification('❌ Arm nicht verfügbar', 'error');
    });
}

function armWeedRemove() {
    fetch('/api/arm/weed_removal', {method: 'POST'})
    .then(r => r.json())
    .then(data => {
        if (data.status === 'sequence_started') {
            showNotification('🌿 Unkraut-Entfernung gestartet', 'success');
        } else {
            showNotification('❌ Sequenz-Fehler', 'error');
        }
    })
    .catch(err => {
        console.error('Weed removal error:', err);
        showNotification('❌ Sequenz fehlgeschlagen', 'error');
    });
}

function updateStatus() {
    fetch('/api/system/status')
    .then(r => r.json())
    .then(data => {
        const statusHtml = `
            <div class="status-item">CPU: ${data.system.cpu_usage}%</div>
            <div class="status-item">RAM: ${data.system.memory_usage}%</div>
            <div class="status-item">Temp: ${data.system.cpu_temperature}°C</div>
            <div class="status-item">Hardware: ${data.hardware.arm_available ? 'Arm OK' : 'Mock'}</div>
        `;
        document.getElementById('system-status').innerHTML = statusHtml;
    })
    .catch(err => {
        console.error('Status error:', err);
        document.getElementById('system-status').innerHTML = '<div class="error">Status nicht verfügbar</div>';
    });
}

// Auto-Update Status
setInterval(updateStatus, 5000);
updateStatus();

console.log('🤖 Dashboard JavaScript geladen');