// app/static/js/camera_complete.js
// KOMPLETTE Kamera-Funktionen - sauber getrennt

console.log('📷 camera_complete.js geladen');

// ===== UTILITY FUNCTIONS =====
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

function updateElement(id, content) {
    const element = document.getElementById(id);
    if (element) {
        element.textContent = content;
    }
}

// ===== CAPTURE FUNCTION =====
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
            // Galerie nach 1 Sekunde neu laden
            setTimeout(function() {
                if (typeof loadImageGallery === 'function') {
                    loadImageGallery();
                }
            }, 1000);
        } else {
            showNotification('❌ Foto-Aufnahme fehlgeschlagen', 'error');
        }
    })
    .catch(error => {
        console.error('Kamera-Fehler:', error);
        showNotification('❌ Kamera-Fehler: ' + error.message, 'error');
    });
}

// ===== GALLERY FUNCTIONS =====
function loadImageGallery() {
    console.log('📁 Lade Bildergalerie...');
    
    fetch('/api/camera/images')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            const gallery = document.getElementById('image-gallery');
            if (!gallery) {
                console.warn('Galerie-Element nicht gefunden');
                return;
            }
            
            console.log(`📁 ${data.count} Bilder gefunden`);
            
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
                                 onclick="openImage('${img.filename}')"
                                 loading="lazy">
                            <button class="delete-cross" 
                                    onclick="deleteImage('${img.filename}')"
                                    title="Löschen">✕</button>
                        </div>
                        <div class="image-info">
                            <div class="image-filename">${img.filename}</div>
                            <div class="image-size">${(img.size / 1024).toFixed(1)} KB</div>
                        </div>
                    </div>
                `;
            });
            
            gallery.innerHTML = html;
            
            // Stats aktualisieren
            updateElement('gallery-count', `${data.count} Bilder`);
            updateElement('gallery-size', `${data.total_size_mb.toFixed(1)} MB`);
            
            // Touch-Support für Delete-Buttons
            addTouchToDeleteButtons();
            
            console.log('✅ Galerie geladen');
        })
        .catch(error => {
            console.error('Galerie-Fehler:', error);
            showNotification('❌ Galerie konnte nicht geladen werden', 'error');
            
            const gallery = document.getElementById('image-gallery');
            if (gallery) {
                gallery.innerHTML = '<div class="no-images">Fehler beim Laden der Galerie</div>';
            }
        });
}

function deleteImage(filename) {
    if (!confirm(`Bild "${filename}" wirklich löschen?`)) return;
    
    console.log(`🗑️ Lösche Bild: ${filename}`);
    
    fetch(`/api/camera/image/${filename}`, {method: 'DELETE'})
        .then(response => response.json())
        .then(data => {
            if (data.status === 'deleted') {
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
    
    console.log('🗑️ Lösche alle Bilder...');
    
    fetch('/api/camera/images/clear', {method: 'POST'})
        .then(response => response.json())
        .then(data => {
            if (data.status === 'cleared') {
                showNotification(`🗑️ ${data.deleted_count} Bilder gelöscht`, 'success');
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
    console.log('💾 Lade alle Bilder herunter...');
    window.open('/api/camera/download_all', '_blank');
}

// ===== OTHER CAMERA FUNCTIONS =====
function detectWeeds() {
    showNotification('🔍 Mock-Unkraut-Erkennung gestartet', 'info');
}

function continuousDetection() {
    showNotification('📹 Mock-Kontinuierliche-Erkennung', 'info');
}

function clearResults() {
    const element = document.getElementById('detection-results');
    if (element) element.textContent = 'Keine Erkennungen';
}

function toggleStream() {
    const streamImg = document.getElementById('camera-stream');
    if (!streamImg) return;
    
    if (streamImg.src.includes('/api/camera/stream')) {
        streamImg.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjQwIiBoZWlnaHQ9IjQ4MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KICA8cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjMjEyMTIxIi8+CiAgPHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCwgc2Fucy1zZXJpZiIgZm9udC1zaXplPSIyNHB4IiBmaWxsPSIjNjY2IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkeT0iLjNlbSI+U3RyZWFtIGdlc3RvcHB0PC90ZXh0Pgo8L3N2Zz4=';
        showNotification('📹 Stream gestoppt', 'info');
    } else {
        streamImg.src = '/api/camera/stream?' + Date.now();
        showNotification('📹 Stream gestartet', 'info');
    }
}

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
        // Foto-Button (wichtigster!)
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
        }
        
        // Andere Buttons
        const buttons = document.querySelectorAll('.btn');
        buttons.forEach(btn => {
            if (btn.id !== 'capture-btn') {
                btn.addEventListener('touchstart', function(e) {
                    this.style.transform = 'scale(0.98)';
                    setTimeout(() => this.style.transform = '', 100);
                }, {passive: true});
                
                btn.style.userSelect = 'none';
                btn.style.webkitUserSelect = 'none';
                btn.style.webkitTouchCallout = 'none';
            }
        });
        
        console.log('✅ Mobile Touch für alle Buttons aktiviert');
    }, 200);
}

function addTouchToDeleteButtons() {
    const deleteButtons = document.querySelectorAll('.delete-cross');
    deleteButtons.forEach(btn => {
        if ('ontouchstart' in window) {
            btn.addEventListener('touchstart', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                // Visuelles Feedback
                this.style.transform = 'scale(1.2)';
                this.style.background = '#ff0000';
                
                setTimeout(() => {
                    this.style.transform = '';
                    this.style.background = '';
                }, 150);
                
                // onClick-Handler ausführen
                if (this.onclick) {
                    this.onclick();
                }
            }, {passive: false});
        }
        
        // Touch-Optimierungen
        btn.style.userSelect = 'none';
        btn.style.webkitUserSelect = 'none';
        btn.style.webkitTouchCallout = 'none';
    });
}

// ===== INITIALIZATION =====
document.addEventListener('DOMContentLoaded', function() {
    console.log('📷 DOM geladen - initialisiere komplette Kamera...');
    
    // Mobile Touch aktivieren
    addMobileTouchSupport();
    
    // Daten laden
    setTimeout(function() {
        if (typeof loadImageGallery === 'function') {
            loadImageGallery();
        }
        if (typeof updateCameraStats === 'function') {
            updateCameraStats();
        }
        
        // Auto-Update alle 30 Sekunden
        setInterval(function() {
            if (typeof updateCameraStats === 'function') {
                updateCameraStats();
            }
        }, 30000);
    }, 1000);
    
    console.log('✅ Komplettes Kamera-System bereit');
});

console.log('📷 camera_complete.js Definition abgeschlossen');