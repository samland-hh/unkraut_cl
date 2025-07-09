// app/static/js/camera_base.js
// NUR die wichtigsten Funktionen - SCHRITT 1

console.log('📷 camera_base.js geladen');

// ===== BASIC FUNCTIONS =====
function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed; 
        top: 20px; 
        right: 20px; 
        background: ${type === 'error' ? '#ff4444' : type === 'success' ? '#44ff44' : '#2196F3'}; 
        color: white; 
        padding: 12px 20px; 
        border-radius: 6px; 
        font-weight: bold; 
        z-index: 10000;
        max-width: 300px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        font-size: 14px;
    `;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(function() {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 3000);
}

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

// ===== MAIN CAPTURE FUNCTION =====
function captureImage() {
    console.log('📸 Foto-Aufnahme gestartet...');
    
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
            throw new Error(`HTTP ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.filename) {
            showNotification(`📸 Foto gespeichert: ${data.filename}`, 'success');
            // loadImageGallery wird später hinzugefügt
        } else {
            showNotification('❌ Foto-Aufnahme fehlgeschlagen', 'error');
        }
    })
    .catch(error => {
        console.error('Kamera-Fehler:', error);
        showNotification('❌ Kamera-Fehler: ' + error.message, 'error');
    });
}

// ===== MOBILE TOUCH SUPPORT =====
function addMobileTouchSupport() {
    if (!('ontouchstart' in window)) {
        console.log('💻 Desktop - kein Touch nötig');
        return;
    }
    
    console.log('📱 Mobile Touch Support wird aktiviert...');
    
    setTimeout(function() {
        const captureBtn = document.getElementById('capture-btn');
        if (captureBtn) {
            captureBtn.addEventListener('touchstart', function(e) {
                e.preventDefault();
                
                // Visuelles Feedback
                this.style.transform = 'scale(0.95)';
                this.style.opacity = '0.8';
                
                setTimeout(() => {
                    this.style.transform = '';
                    this.style.opacity = '';
                }, 150);
                
                // Foto aufnehmen
                captureImage();
                
            }, {passive: false});
            
            // Touch-Optimierungen
            captureBtn.style.userSelect = 'none';
            captureBtn.style.webkitUserSelect = 'none';
            captureBtn.style.webkitTouchCallout = 'none';
            captureBtn.style.touchAction = 'manipulation';
            
            console.log('✅ Mobile Touch für Foto-Button aktiviert');
        } else {
            console.warn('❌ Foto-Button nicht gefunden!');
        }
    }, 100);
}

// ===== INITIALIZATION =====
document.addEventListener('DOMContentLoaded', function() {
    console.log('📷 DOM geladen - initialisiere Kamera...');
    
    // Mobile Touch aktivieren
    addMobileTouchSupport();
    
    console.log('✅ Basis-Kamera-System bereit');
});

console.log('📷 camera_base.js Definition abgeschlossen');