// app/static/js/camera.js
// Kamera JavaScript mit Mobile Touch Support - FIXED VERSION

/* ========== MOBILE TOUCH EVENT SYSTEM ========== */
function attachMobileEvents(element, handler) {
    if (!element) return;
    
    let touchHandled = false;
    
    function safeHandler(e) {
        if (touchHandled) return;
        
        touchHandled = true;
        e.preventDefault();
        e.stopPropagation();
        
        // Visuelles Feedback für Mobile
        const originalTransform = element.style.transform;
        const originalBackground = element.style.background;
        
        element.style.transform = 'scale(0.95)';
        element.style.background = 'rgba(255,255,255,0.2)';
        
        setTimeout(() => {
            element.style.transform = originalTransform;
            element.style.background = originalBackground;
        }, 150);
        
        // Handler ausführen
        if (typeof handler === 'function') {
            handler();
        } else if (element.onclick) {
            element.onclick();
        }
        
        // Reset für nächsten Touch
        setTimeout(() => {
            touchHandled = false;
        }, 600);
    }
    
    // Events für Desktop UND Mobile
    element.addEventListener('click', safeHandler, {passive: false});
    element.addEventListener('touchstart', safeHandler, {passive: false});
    
    // Touch-Optimierungen
    element.style.userSelect = 'none';
    element.style.webkitUserSelect = 'none';
    element.style.webkitTouchCallout = 'none';
    element.style.touchAction = 'manipulation';
}

/* ========== NOTIFICATION SYSTEM ========== */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = 'notification notification-' + type;
    
    const colors = {
        error: '#ff4444',
        success: '#44ff44',
        warning: '#ffaa44',
        info: '#2196F3'
    };
    
    notification.style.cssText = `
        position: fixed; 
        top: 20px; 
        right: 20px; 
        background: ${colors[type] || colors.info}; 
        color: white; 
        padding: 12px 20px; 
        border-radius: 6px; 
        font-weight: bold; 
        z-index: 10000;
        max-width: 300px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        font-size: 14px;
        animation: slideIn 0.3s ease-out;
    `;
    
    notification.textContent = message;
    document.body.appendChild(notification);
    
    // Auto-remove
    setTimeout(() => {
        if (notification.parentNode) {
            notification.style.animation = 'slideOut 0.3s ease-in';
            setTimeout(() => notification.remove(), 300);
        }
    }, 3000);
    
    console.log(`[${type.toUpperCase()}] ${message}`);
}

/* ========== UTILITY FUNCTIONS ========== */
function generateTimestamp() {
    const now = new Date();
    const pad = (n) => String(n).padStart(2, '0');
    
    return [
        String(now.getFullYear()).slice(-2),
        pad(now.getMonth() + 1),
        pad(now.getDate()),
        pad(now.getHours()),
        pad(now.getMinutes()),
        pad(now.getSeconds())
    ].join('.');
}

function updateElement(id, content) {
    const element = document.getElementById(id);
    if (element) {
        element.textContent = content;
    }
}

/* ========== KAMERA FUNKTIONEN ========== */
function captureImage() {
    console.log('📸 Foto-Aufnahme gestartet...');
    showNotification('📸 Nehme Foto auf...', 'info');
    
    const filename = 'img_' + generateTimestamp() + '.jpg';
    
    fetch('/api/camera/capture', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({filename: filename})
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.filename) {
            showNotification(`📸 Foto gespeichert: ${data.filename}`, 'success');
            setTimeout(loadImageGallery, 1000);
        } else {
            showNotification('❌ Foto-Aufnahme fehlgeschlagen', 'error');
        }
    })
    .catch(error => {
        console.error('Kamera-Fehler:', error);
        showNotification('❌ Kamera-Fehler: ' + error.message, 'error');
    });
}

function toggleStream() {
    const streamImg = document.getElementById('camera-stream');
    if (!streamImg) return;
    
    if (streamImg.src.includes('/api/camera/stream')) {
        streamImg.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjQwIiBoZWlnaHQ9IjQ4MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KICA8cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjMjEyMTIxIi8+CiAgPHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCwgc2Fucy1zZXJpZiIgZm9udC1zaXplPSIyNHB4IiBmaWxsPSIjNjY2IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkeT0iLjNlbSI+U3RyZWFtIGdlc3RvcHB0PC90ZXh0Pgo8L3N2Zz4=';
        showNotification('📹 Stream gestoppt', 'info');
    } else {
        streamImg.src = '/api/camera/stream?' + Date.now(); // Cache-Buster
        showNotification('📹 Stream gestartet', 'info');
    }
}

/* ========== SYSTEM STATUS ========== */
function updateCameraStats() {
    fetch('/api/system/status')
        .then(response => response.json())
        .then(data => {
            updateElement('cpu-usage', data.system.cpu_usage + '%');
            updateElement('ram-usage', data.system.memory_usage + '%');
            updateElement('cpu-temp', data.system.cpu_temperature + '°C');
            updateElement('camera-status', data.hardware.camera_available ? 'Online' : 'Offline');
            updateElement('arm-status', data.hardware.arm_available ? 'Verfügbar' : 'Mock');
            updateElement('stream-fps', '30 FPS');
        })
        .catch(error => {
            console.warn('Status-Update Fehler:', error);
            // Stumm bei Fehlern
        });
}

/* ========== BILDERGALERIE ========== */
function loadImageGallery() {
    fetch('/api/camera/images')
        .then(response => response.json())
        .then(data => {
            const gallery = document.getElementById('image-gallery');
            if (!gallery) return;
            
            if (!data.images || data.images.length === 0) {
                gallery.innerHTML = '<div class="no-images">Keine Bilder aufgenommen</div>';
                updateElement('gallery-count', '0 Bilder');
                updateElement('gallery-size', '0 MB');
                return;
            }
            
            let html = '';
            data.images.forEach(img => {
                html += `
                    <div class="gallery-item">
                        <div class="gallery-image-container">
                            <img src="/api/camera/image/${img.filename}" 
                                 class="gallery-image" 
                                 alt="${img.filename}" 
                                 onclick="openImage('${img.filename}')">
                            <button class="delete-cross" 
                                    data-filename="${img.filename}"
                                    title="Löschen">✕</button>
                        </div>
                        <div class="image-info">
                            <div class="image-filename">${img.filename}</div>
                        </div>
                    </div>
                `;
            });
            
            gallery.innerHTML = html;
            
            updateElement('gallery-count', data.images.length + ' Bilder');
            updateElement('gallery-size', (data.total_size_mb || 0).toFixed(1) + ' MB');
            
            // WICHTIG: Mobile Touch-Events für Delete-Buttons
            document.querySelectorAll('.delete-cross').forEach(btn => {
                const filename = btn.dataset.filename;
                attachMobileEvents(btn, () => deleteImage(filename));
            });
        })
        .catch(error => {
            console.error('Galerie-Fehler:', error);
            showNotification('❌ Galerie-Laden fehlgeschlagen', 'error');
        });
}

function deleteImage(filename) {
    if (!confirm(`Bild "${filename}" wirklich löschen?`)) return;
    
    fetch(`/api/camera/image/${filename}`, {method: 'DELETE'})
        .then(response => {
            if (response.ok) {
                showNotification('🗑️ Bild gelöscht', 'success');
                loadImageGallery();
            } else {
                showNotification('❌ Löschen fehlgeschlagen', 'error');
            }
        })
        .catch(error => {
            console.error('Delete-Fehler:', error);
            showNotification('❌ Löschen fehlgeschlagen', 'error');
        });
}

function clearImages() {
    if (!confirm('Wirklich ALLE Bilder löschen?')) return;
    
    fetch('/api/camera/images/clear', {method: 'POST'})
        .then(response => {
            if (response.ok) {
                showNotification('🗑️ Alle Bilder gelöscht', 'success');
                loadImageGallery();
            } else {
                showNotification('❌ Löschen fehlgeschlagen', 'error');
            }
        })
        .catch(error => {
            console.error('Clear-Fehler:', error);
            showNotification('❌ Löschen fehlgeschlagen', 'error');
        });
}

function openImage(filename) {
    window.open(`/api/camera/image/${filename}`, '_blank');
}

function downloadImages() {
    window.open('/api/camera/download_all', '_blank');
}

/* ========== UNKRAUT-ERKENNUNG (DUMMY) ========== */
function detectWeeds() {
    showNotification('🔍 Mock-Unkraut-Erkennung gestartet', 'info');
    
    // Simulate detection
    setTimeout(() => {
        const results = document.getElementById('detection-results');
        if (results) {
            results.textContent = `Letzte Erkennung: ${new Date().toLocaleTimeString()}\n2 Unkraut-Bereiche erkannt\nPosition: (120, 85), (340, 220)`;
        }
        showNotification('🌿 Unkraut-Erkennung abgeschlossen', 'success');
    }, 2000);
}

function continuousDetection() {
    showNotification('📹 Mock-Kontinuierliche-Erkennung', 'info');
}

function clearResults() {
    const element = document.getElementById('detection-results');
    if (element) {
        element.textContent = 'Keine Erkennungen';
    }
    showNotification('🗑️ Erkennungsergebnisse gelöscht', 'info');
}

/* ========== INITIALIZATION ========== */
document.addEventListener('DOMContentLoaded', function() {
    console.log('📱 Kamera JavaScript geladen - Mobile Touch Support aktiviert');
    
    // Feature Detection
    const hasTouch = 'ontouchstart' in window;
    const isMobile = /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    
    console.log(`Touch Support: ${hasTouch}, Mobile: ${isMobile}`);
    
    // Initiale Daten laden
    updateCameraStats();
    loadImageGallery();
    
    // Auto-Update alle 10 Sekunden
    setInterval(updateCameraStats, 10000);
    
    // WICHTIG: Mobile Touch-Events für alle wichtigen Buttons aktivieren
    setTimeout(() => {
        // Foto-Button (wichtigster Button!)
        const captureButtons = [
            document.querySelector('button[onclick*="captureImage"]'),
            document.querySelector('button[onclick="captureImage()"]'),
            ...document.querySelectorAll('button')
        ].filter(btn => btn && (btn.textContent || '').includes('📸'));
        
        captureButtons.forEach(btn => {
            if (btn) {
                console.log('📱 Mobile Touch für Foto-Button aktiviert');
                attachMobileEvents(btn, captureImage);
            }
        });
        
        // Weitere wichtige Buttons
        const buttonSelectors = [
            'button[onclick*="clearImages"]',
            'button[onclick*="downloadImages"]',
            'button[onclick*="loadImageGallery"]',
            'button[onclick*="toggleStream"]',
            'button[onclick*="detectWeeds"]',
            'button[onclick*="continuousDetection"]',
            'button[onclick*="clearResults"]'
        ];
        
        buttonSelectors.forEach(selector => {
            const btn = document.querySelector(selector);
            if (btn) {
                attachMobileEvents(btn, () => {}); // Handler via onclick schon da
            }
        });
        
        console.log('📱 Mobile Touch-Events für alle Buttons aktiviert');
    }, 500);
    
    // Stream Error Handling
    const cameraStream = document.getElementById('camera-stream');
    if (cameraStream) {
        cameraStream.addEventListener('error', function() {
            this.alt = 'Kamera nicht verfügbar';
            showNotification('📷 Kamera-Stream unterbrochen', 'warning');
        });
        
        cameraStream.addEventListener('load', function() {
            console.log('📹 Kamera-Stream geladen');
        });
    }
    
    showNotification('📷 Kamera-Interface bereit', 'success');
});

/* ========== CSS ANIMATIONS ========== */
// CSS Animations für Notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    
    .notification {
        animation: slideIn 0.3s ease-out;
    }
`;
document.head.appendChild(style);