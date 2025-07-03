// app/static/js/common.js - Gemeinsame JavaScript Funktionen

// Notification System
function showNotification(message, type = 'info') {
    // Entferne existierende Notifications
    const existing = document.querySelector('.notification');
    if (existing) {
        existing.remove();
    }
    
    // Erstelle neue Notification
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Styles für Notification
    Object.assign(notification.style, {
        position: 'fixed',
        top: '20px',
        right: '20px',
        padding: '15px 20px',
        borderRadius: '8px',
        color: 'white',
        fontWeight: 'bold',
        zIndex: '9999',
        opacity: '0',
        transform: 'translateY(-20px)',
        transition: 'all 0.3s ease',
        maxWidth: '300px',
        wordWrap: 'break-word'
    });
    
    // Farben je nach Type
    const colors = {
        success: '#28a745',
        error: '#dc3545',
        warning: '#ffc107',
        info: '#17a2b8'
    };
    
    notification.style.backgroundColor = colors[type] || colors.info;
    
    // Zu DOM hinzufügen
    document.body.appendChild(notification);
    
    // Animation einblenden
    setTimeout(() => {
        notification.style.opacity = '1';
        notification.style.transform = 'translateY(0)';
    }, 100);
    
    // Nach 4 Sekunden entfernen
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateY(-20px)';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 4000);
}

// Kamera Stream Error Handling
function setupCameraErrorHandling() {
    const cameraStream = document.getElementById('camera-stream');
    if (cameraStream) {
        cameraStream.addEventListener('error', function() {
            this.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjQwIiBoZWlnaHQ9IjQ4MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjMzMzIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxOCIgZmlsbD0iI2ZmZiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPvCfk7kgS2FtZXJhIG5pY2h0IHZlcmbDvGdiYXI8L3RleHQ+PC9zdmc+';
            this.alt = 'Kamera nicht verfügbar';
            showNotification('📷 Kamera-Stream unterbrochen', 'warning');
        });
        
        cameraStream.addEventListener('load', function() {
            console.log('📹 Kamera-Stream geladen');
        });
    }
}

// API Helper Functions
async function apiRequest(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error(`API Request failed: ${url}`, error);
        throw error;
    }
}

// Touch Support für Mobile
function setupTouchSupport() {
    if ('ontouchstart' in window) {
        document.querySelectorAll('.btn').forEach(btn => {
            btn.addEventListener('touchstart', function(e) {
                e.preventDefault();
                this.classList.add('active');
            });
            
            btn.addEventListener('touchend', function(e) {
                e.preventDefault();
                this.classList.remove('active');
            });
        });
        
        console.log('📱 Touch-Support aktiviert');
    }
}

// Keyboard Shortcuts
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Nur wenn kein Input-Feld fokussiert ist
        if (document.activeElement.tagName === 'INPUT' || document.activeElement.tagName === 'TEXTAREA') {
            return;
        }
        
        switch(e.code) {
            case 'Space':
                e.preventDefault();
                if (typeof stopAll === 'function') {
                    stopAll();
                }
                break;
            case 'KeyH':
                if (typeof armHome === 'function') {
                    armHome();
                }
                break;
            case 'KeyC':
                if (typeof captureImage === 'function') {
                    captureImage();
                }
                break;
            case 'KeyD':
                if (typeof detectWeeds === 'function') {
                    detectWeeds();
                }
                break;
        }
    });
    
    console.log('⌨️ Tastatur-Shortcuts aktiviert (Space=Stop, H=Home, C=Capture, D=Detect)');
}

// Connection Monitor
function startConnectionMonitor() {
    let isOnline = true;
    
    async function checkConnection() {
        try {
            await fetch('/api/system/status', { 
                method: 'HEAD',
                cache: 'no-cache'
            });
            
            if (!isOnline) {
                isOnline = true;
                showNotification('✅ Verbindung wiederhergestellt', 'success');
            }
        } catch (error) {
            if (isOnline) {
                isOnline = false;
                showNotification('❌ Verbindung unterbrochen', 'error');
            }
        }
    }
    
    // Prüfe alle 10 Sekunden
    setInterval(checkConnection, 10000);
    console.log('🔗 Verbindungsmonitor gestartet');
}

// Format Helper Functions
function formatTimestamp(timestamp) {
    return new Date(timestamp * 1000).toLocaleString('de-DE');
}

function formatBytes(bytes) {
    const units = ['B', 'KB', 'MB', 'GB'];
    let i = 0;
    while (bytes >= 1024 && i < units.length - 1) {
        bytes /= 1024;
        i++;
    }
    return `${bytes.toFixed(1)} ${units[i]}`;
}

function formatDuration(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
        return `${hours}h ${minutes}m ${secs}s`;
    } else if (minutes > 0) {
        return `${minutes}m ${secs}s`;
    } else {
        return `${secs}s`;
    }
}

// Initialize Common Features
document.addEventListener('DOMContentLoaded', function() {
    setupCameraErrorHandling();
    setupTouchSupport();
    setupKeyboardShortcuts();
    startConnectionMonitor();
    
    console.log('🚀 Unkraut-2025 Common JavaScript geladen');
});