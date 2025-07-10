// unkraut/app/static/js/dashboard.js
// Dashboard-spezifische JavaScript-Funktionen

// System-Status aktualisieren
function updateStatus() {
    fetch('/api/system/status')
        .then(response => response.json())
        .then(data => {
            document.getElementById('system-status').innerHTML = 
                `CPU: ${data.system?.cpu_usage || 'N/A'}%<br>RAM: ${data.system?.memory_usage || 'N/A'}%<br>Temp: ${data.system?.cpu_temperature || 'N/A'}°C`;
        })
        .catch(error => {
            document.getElementById('system-status').innerHTML = '❌ Status nicht verfügbar';
        });
}

// Kamera-Funktionen
function captureImage() {
    showNotification('📸 Foto wird aufgenommen...', 'info');
    
    fetch('/api/camera/capture', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                showNotification('✅ Foto gespeichert', 'success');
            } else {
                showNotification('❌ Foto-Fehler', 'error');
            }
        })
        .catch(error => {
            showNotification('❌ Foto-Fehler', 'error');
        });
}

function detectWeeds() {
    showNotification('🔍 Unkrauterkennung läuft...', 'info');
    
    fetch('/api/ai/detect', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.detections && data.detections.length > 0) {
                showNotification(`🌿 ${data.detections.length} Unkraut gefunden`, 'success');
            } else {
                showNotification('✅ Kein Unkraut erkannt', 'success');
            }
        })
        .catch(error => {
            showNotification('❌ Erkennungsfehler', 'error');
        });
}

// Roboter-Steuerung
function moveRobot(direction) {
    fetch('/api/control/move', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ direction: direction, speed: 50, duration: 1.0 })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showNotification(`🚗 Fahre ${direction}`, 'info');
        }
    })
    .catch(error => {
        showNotification('❌ Bewegungsfehler', 'error');
    });
}

function stopAll() {
    fetch('/api/control/stop', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            showNotification('⏹️ Alle Motoren gestoppt', 'warning');
        })
        .catch(error => {
            showNotification('❌ Stopp-Fehler', 'error');
        });
}

// Roboterarm-Steuerung
function armHome() {
    fetch('/api/arm/home', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            showNotification('🏠 Arm fährt zur Home-Position', 'info');
        })
        .catch(error => {
            showNotification('❌ Arm-Fehler', 'error');
        });
}

function armWeedRemove() {
    fetch('/api/arm/move/preset', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ preset: 'weed_removal' })
    })
    .then(response => response.json())
    .then(data => {
        showNotification('🌿 Unkraut-Entfernung gestartet', 'info');
    })
    .catch(error => {
        showNotification('❌ Arm-Fehler', 'error');
    });
}

// System-Steuerung Modal-Funktionen
function parkAndShutdown() {
    document.getElementById('shutdown-modal').style.display = 'flex';
}

function systemReboot() {
    document.getElementById('reboot-modal').style.display = 'flex';
}

function emergencyShutdown() {
    document.getElementById('emergency-modal').style.display = 'flex';
}

function closeShutdownModal() {
    document.getElementById('shutdown-modal').style.display = 'none';
}

function closeRebootModal() {
    document.getElementById('reboot-modal').style.display = 'none';
}

function closeEmergencyModal() {
    document.getElementById('emergency-modal').style.display = 'none';
}

// System-Steuerung Bestätigung-Funktionen
function confirmShutdown() {
    const btn = document.getElementById('shutdown-btn');
    btn.disabled = true;
    btn.classList.add('loading');
    
    closeShutdownModal();
    showNotification('🔄 System wird heruntergefahren...', 'warning');
    
    fetch('/api/system/shutdown', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'shutdown_initiated') {
                showNotification('🔴 Shutdown gestartet - System schaltet sich aus', 'warning');
                startCountdown(10, 'System schaltet sich aus');
            } else {
                showNotification('❌ Shutdown-Fehler', 'error');
                btn.disabled = false;
                btn.classList.remove('loading');
            }
        })
        .catch(error => {
            showNotification('❌ Shutdown-Fehler', 'error');
            btn.disabled = false;
            btn.classList.remove('loading');
        });
}

function confirmReboot() {
    const btn = document.getElementById('reboot-btn');
    btn.disabled = true;
    btn.classList.add('loading');
    
    closeRebootModal();
    showNotification('🔄 System wird neu gestartet...', 'info');
    
    fetch('/api/system/reboot', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'reboot_initiated') {
                showNotification('🔄 Reboot gestartet - System startet neu', 'info');
                startCountdown(15, 'System startet neu');
            } else {
                showNotification('❌ Reboot-Fehler', 'error');
                btn.disabled = false;
                btn.classList.remove('loading');
            }
        })
        .catch(error => {
            showNotification('❌ Reboot-Fehler', 'error');
            btn.disabled = false;
            btn.classList.remove('loading');
        });
}

function confirmEmergencyShutdown() {
    const btn = document.getElementById('emergency-shutdown-btn');
    btn.disabled = true;
    btn.classList.add('loading');
    
    closeEmergencyModal();
    showNotification('🚨 NOT-SHUTDOWN aktiviert!', 'error');
    
    fetch('/api/system/emergency_shutdown', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            showNotification('🚨 NOT-SHUTDOWN! System schaltet sich sofort aus!', 'error');
        })
        .catch(error => {
            showNotification('🚨 NOT-SHUTDOWN aktiviert (Fehler ignoriert)', 'error');
        });
}

// Hilfsfunktionen
function startCountdown(seconds, message) {
    let countdown = seconds;
    const interval = setInterval(() => {
        showNotification(`🔴 ${message} in ${countdown}s`, 'warning');
        countdown--;
        if (countdown < 0) {
            clearInterval(interval);
            showNotification(`🔴 ${message}...`, 'error');
        }
    }, 1000);
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    // Styles für Notification
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem;
        border-radius: 5px;
        color: white;
        z-index: 1001;
        max-width: 300px;
        font-weight: bold;
        animation: slideIn 0.3s ease-out;
    `;
    
    // Farben je nach Type
    const colors = {
        info: '#007bff',
        success: '#28a745',
        warning: '#ffc107',
        error: '#dc3545'
    };
    
    notification.style.backgroundColor = colors[type] || colors.info;
    
    document.body.appendChild(notification);
    
    // Auto-remove nach 5 Sekunden
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-in';
        setTimeout(() => {
            if (document.body.contains(notification)) {
                document.body.removeChild(notification);
            }
        }, 300);
    }, 5000);
}

// Initialisierung
document.addEventListener('DOMContentLoaded', function() {
    // Status regelmäßig aktualisieren
    setInterval(updateStatus, 5000);
    
    // Initial Status laden
    updateStatus();
});