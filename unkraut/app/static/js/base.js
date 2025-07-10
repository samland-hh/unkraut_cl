// unkraut/app/static/js/base.js
// Base-Template JavaScript mit Shutdown-Timer

// Timer-Variablen
let timerInterval = null;
let connectionCheckInterval = null;

// Initialisierung
document.addEventListener('DOMContentLoaded', function() {
    startShutdownTimer();
    startConnectionCheck();
    updateMobileTime();
    setInterval(updateMobileTime, 1000);
});

// === SHUTDOWN-TIMER ===
function startShutdownTimer() {
    // Sofort laden
    updateShutdownTimer();
    
    // Alle 60 Sekunden aktualisieren
    if (timerInterval) {
        clearInterval(timerInterval);
    }
    
    timerInterval = setInterval(updateShutdownTimer, 60000); // 1 Minute
}

function updateShutdownTimer() {
    fetch('/api/system/uptime')
        .then(response => response.json())
        .then(data => {
            const timerDisplay = document.getElementById('timer-display');
            const shutdownTimer = document.getElementById('shutdown-timer');
            
            if (timerDisplay && shutdownTimer) {
                // Zeit anzeigen
                timerDisplay.textContent = data.remaining_formatted || '--:--';
                
                // Farb-Warnungen basierend auf Script-kompatiblem Status
                shutdownTimer.className = 'shutdown-timer';
                
                if (data.warning_status === 'critical') {
                    shutdownTimer.classList.add('critical');
                } else if (data.warning_status === 'warning') {
                    shutdownTimer.classList.add('warning');
                }
                
                // Tooltip mit Details (wie im auto_shutdown.sh Script)
                const bootTime = new Date(data.boot_time * 1000).toLocaleString('de-DE');
                shutdownTimer.title = `Auto-Shutdown in ${data.remaining_formatted}\nBoot-Zeit: ${bootTime}\nScript-kompatibel: ${data.script_compatible}`;
            }
        })
        .catch(error => {
            console.error('Timer-Update-Fehler:', error);
            const timerDisplay = document.getElementById('timer-display');
            if (timerDisplay) {
                timerDisplay.textContent = '--:--';
            }
        });
}

// === CONNECTION CHECK ===
function startConnectionCheck() {
    checkConnection();
    
    if (connectionCheckInterval) {
        clearInterval(connectionCheckInterval);
    }
    
    connectionCheckInterval = setInterval(checkConnection, 30000); // 30 Sekunden
}

function checkConnection() {
    const indicator = document.getElementById('connection-indicator');
    
    if (indicator) {
        fetch('/api/system/status', { 
            method: 'HEAD',
            timeout: 5000
        })
        .then(() => {
            indicator.textContent = '🟢';
            indicator.title = 'Verbindung OK';
        })
        .catch(() => {
            indicator.textContent = '🔴';
            indicator.title = 'Verbindung unterbrochen';
        });
    }
}

// === MOBILE TIME ===
function updateMobileTime() {
    const mobileTime = document.getElementById('mobile-time');
    if (mobileTime) {
        const now = new Date();
        const timeString = now.toLocaleTimeString('de-DE', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
        mobileTime.textContent = timeString;
    }
}

// === NAVIGATION ===
function navigateTo(path) {
    try {
        console.log('Navigate to:', path);
        window.location.href = path;
    } catch (error) {
        console.error('Navigation error:', error);
        showNotification('Navigationsfehler: ' + error.message, 'error');
    }
}

// === NOTIFICATION SYSTEM ===
function showNotification(message, type = 'info') {
    // Entferne bestehende Notifications
    const existing = document.querySelector('.notification');
    if (existing) {
        existing.remove();
    }
    
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    // Styles
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
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
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

// === TIMER-FUNKTIONEN (für andere Seiten) ===
function getShutdownTimeRemaining() {
    return fetch('/api/system/uptime')
        .then(response => response.json())
        .then(data => data.remaining_seconds)
        .catch(() => 0);
}

function formatTime(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`;
}

// === CLEANUP ===
window.addEventListener('beforeunload', function() {
    if (timerInterval) {
        clearInterval(timerInterval);
    }
    if (connectionCheckInterval) {
        clearInterval(connectionCheckInterval);
    }
});

// === EXPORTS ===
window.unkrautBase = {
    updateShutdownTimer,
    getShutdownTimeRemaining,
    formatTime,
    showNotification,
    navigateTo
};