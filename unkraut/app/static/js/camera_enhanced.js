// unkraut/app/static/js/camera_enhanced.js

/**
 * Clean Camera JavaScript - Overlay entfernt, img_ Dateinamen, Kreuz-Button
 * Gemäß Unkraut-2025 Projekt-Richtlinien: Klare Trennung HTML/CSS/JS
 */

// Globale Variablen
let continuousDetectionActive = false;
let galleryImages = [];
let statsUpdateInterval = null;

// Klasse für Camera Controller
class CameraController {
    constructor() {
        this.isInitialized = false;
        this.init();
    }
    
    init() {
        this.bindEventListeners();
        this.setupAutoUpdates();
        this.isInitialized = true;
        console.log('📹 Clean Camera Controller initialisiert');
    }
    
    bindEventListeners() {
        // Auto-Load beim Seitenstart
        document.addEventListener('DOMContentLoaded', () => {
            this.updateCameraStats();
            this.loadImageGallery();
        });
        
        // Stream Error Handling
        const streamImg = document.getElementById('camera-stream');
        if (streamImg) {
            streamImg.addEventListener('error', () => {
                console.warn('❌ Kamera-Stream Fehler');
                this.showNotification('❌ Stream-Verbindung unterbrochen', 'error');
            });
            
            streamImg.addEventListener('load', () => {
                console.log('📹 Kamera-Stream aktiv');
            });
        }
    }
    
    setupAutoUpdates() {
        // Auto-Update Stats alle 10 Sekunden
        if (statsUpdateInterval) {
            clearInterval(statsUpdateInterval);
        }
        
        statsUpdateInterval = setInterval(() => {
            this.updateCameraStats();
        }, 10000);
        
        console.log('📊 Auto-Update Stats gestartet (10s Intervall)');
    }
    
    async updateCameraStats() {
        try {
            const response = await fetch('/api/system/status');
            const data = await response.json();
            
            // System-Stats aktualisieren
            this.updateElement('cpu-usage', `${data.system.cpu_usage}%`);
            this.updateElement('ram-usage', `${data.system.memory_usage}%`);
            this.updateElement('cpu-temp', `${data.system.cpu_temperature}°C`);
            
            // Hardware-Status
            this.updateElement('camera-status', 
                data.hardware.camera_available ? 'Online' : 'Offline');
            this.updateElement('arm-status', 
                data.hardware.arm_available ? 'Verfügbar' : 'Mock');
            this.updateElement('stream-fps', '30 FPS');
            
            console.log('📊 Kamera-Statistiken aktualisiert');
            
        } catch (error) {
            console.error('❌ Stats-Update-Fehler:', error);
            // Fallback-Werte setzen
            this.updateElement('cpu-usage', 'N/A');
            this.updateElement('ram-usage', 'N/A');
            this.updateElement('cpu-temp', 'N/A');
            this.updateElement('camera-status', 'Unbekannt');
            this.updateElement('arm-status', 'Unbekannt');
        }
    }
    
    updateElement(id, content) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = content;
        }
    }
    
    async captureImage() {
        try {
            this.showNotification('📸 Nehme Foto auf...', 'info');
            
            // Custom Dateiname mit img_ Prefix erstellen
            const now = new Date();
            const yy = String(now.getFullYear()).slice(-2);
            const mm = String(now.getMonth() + 1).padStart(2, '0');
            const dd = String(now.getDate()).padStart(2, '0');
            const hh = String(now.getHours()).padStart(2, '0');
            const min = String(now.getMinutes()).padStart(2, '0');
            const ss = String(now.getSeconds()).padStart(2, '0');
            const timestamp = `${yy}.${mm}.${dd}_${hh}.${min}_${ss}`;
            
            const customFilename = `img_${timestamp}.jpg`;
            
            const response = await fetch('/api/camera/capture', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    filename: customFilename
                })
            });
            const data = await response.json();
            
            if (data.filename) {
                this.showNotification(`📸 Foto gespeichert: ${data.filename}`, 'success');
                // Galerie automatisch aktualisieren
                setTimeout(() => this.loadImageGallery(), 1000);
            } else {
                this.showNotification('❌ Foto-Aufnahme fehlgeschlagen', 'error');
            }
        } catch (error) {
            console.error('❌ Capture-Fehler:', error);
            this.showNotification('❌ Kamera-Fehler', 'error');
        }
    }
    
    async detectWeeds() {
        try {
            this.showNotification('🔍 Analysiere Bild...', 'info');
            
            const response = await fetch('/api/ai/detect', {
                method: 'POST'
            });
            const data = await response.json();
            
            this.displayDetectionResults(data);
            
        } catch (error) {
            console.error('❌ Detection-Fehler:', error);
            this.showNotification('❌ KI-Analyse fehlgeschlagen', 'error');
        }
    }
    
    displayDetectionResults(data) {
        const resultsElement = document.getElementById('detection-results');
        if (!resultsElement) return;
        
        // CSS-Klassen zurücksetzen
        resultsElement.className = 'detection-display';
        
        if (data.weeds && data.weeds.length > 0) {
            let resultText = `🔍 UNKRAUT ERKANNT (${data.weeds.length} Objekte):\n\n`;
            
            data.weeds.forEach((weed, index) => {
                resultText += `${index + 1}. Position: (${weed.x}, ${weed.y})\n`;
                resultText += `   Größe: ${weed.width}x${weed.height}\n`;
                resultText += `   Vertrauen: ${(weed.confidence * 100).toFixed(1)}%\n\n`;
            });
            
            if (data.arm_action) {
                resultText += `🦾 Roboterarm: ${data.arm_action}\n`;
            }
            
            resultsElement.textContent = resultText;
            resultsElement.classList.add('has-results');
            
        } else {
            resultsElement.textContent = '✅ Kein Unkraut erkannt';
            resultsElement.style.borderColor = '#2196F3';
            resultsElement.style.background = 'rgba(33, 150, 243, 0.1)';
        }
    }
    
    toggleContinuousDetection() {
        continuousDetectionActive = !continuousDetectionActive;
        
        if (continuousDetectionActive) {
            this.showNotification('📹 Kontinuierliche Erkennung gestartet', 'info');
            this.startContinuousDetection();
        } else {
            this.showNotification('⏹️ Kontinuierliche Erkennung gestoppt', 'info');
        }
    }
    
    async startContinuousDetection() {
        if (!continuousDetectionActive) return;
        
        try {
            await this.detectWeeds();
        } catch (error) {
            console.error('❌ Kontinuierliche Erkennung Fehler:', error);
        }
        
        // Nächste Erkennung nach 3 Sekunden
        if (continuousDetectionActive) {
            setTimeout(() => this.startContinuousDetection(), 3000);
        }
    }
    
    async loadImageGallery() {
        try {
            const response = await fetch('/api/camera/images');
            const data = await response.json();
            
            galleryImages = data.images || [];
            this.renderGallery();
            
            // Stats aktualisieren
            this.updateElement('gallery-count', `${galleryImages.length} Bilder`);
            this.updateElement('gallery-size', `${(data.total_size_mb || 0).toFixed(1)} MB`);
            
        } catch (error) {
            console.error('❌ Galerie-Laden-Fehler:', error);
            this.showNotification('❌ Galerie konnte nicht geladen werden', 'error');
        }
    }
    
    renderGallery() {
        const gallery = document.getElementById('image-gallery');
        if (!gallery) return;
        
        if (galleryImages.length === 0) {
            gallery.innerHTML = '<div class="no-images">Keine Bilder aufgenommen</div>';
            return;
        }
        
        // Neue Galerie-HTML mit Kreuz-Button auf dem Bild
        const galleryHTML = galleryImages.map(image => `
            <div class="gallery-item">
                <div class="gallery-image-container">
                    <img src="/api/camera/image/${image.filename}" 
                         alt="${image.filename}" 
                         class="gallery-image"
                         onclick="cameraController.openImageModal('${image.filename}')">
                    <button class="delete-cross" 
                            onclick="event.stopPropagation(); cameraController.deleteImage('${image.filename}')"
                            title="Bild löschen">
                    </button>
                </div>
                <div class="image-info">
                    <div class="image-filename">${image.filename}</div>
                </div>
            </div>
        `).join('');
        
        gallery.innerHTML = galleryHTML;
    }
    
    async deleteImage(filename) {
        if (!confirm(`Bild "${filename}" wirklich löschen?`)) return;
        
        try {
            const response = await fetch(`/api/camera/image/${filename}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                this.showNotification(`🗑️ Bild "${filename}" gelöscht`, 'success');
                this.loadImageGallery();
            } else {
                this.showNotification('❌ Löschen fehlgeschlagen', 'error');
            }
        } catch (error) {
            console.error('❌ Delete-Fehler:', error);
            this.showNotification('❌ Löschen fehlgeschlagen', 'error');
        }
    }
    
    async clearAllImages() {
        if (!confirm('Wirklich ALLE Bilder löschen?')) return;
        
        try {
            const response = await fetch('/api/camera/images/clear', {
                method: 'POST'
            });
            
            if (response.ok) {
                this.showNotification('🗑️ Alle Bilder gelöscht', 'success');
                this.loadImageGallery();
            } else {
                this.showNotification('❌ Löschen fehlgeschlagen', 'error');
            }
        } catch (error) {
            console.error('❌ Clear-All-Fehler:', error);
            this.showNotification('❌ Löschen fehlgeschlagen', 'error');
        }
    }
    
    clearResults() {
        const resultsElement = document.getElementById('detection-results');
        if (resultsElement) {
            resultsElement.textContent = 'Keine Erkennungen';
            resultsElement.className = 'detection-display';
        }
    }
    
    toggleStream() {
        const streamImg = document.getElementById('camera-stream');
        if (!streamImg) return;
        
        if (streamImg.src.includes('/api/camera/stream')) {
            // Stream stoppen - Placeholder anzeigen
            streamImg.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjQwIiBoZWlnaHQ9IjQ4MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KICA8cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjMjEyMTIxIi8+CiAgPHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCwgc2Fucy1zZXJpZiIgZm9udC1zaXplPSIyNHB4IiBmaWxsPSIjNjY2IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkeT0iLjNlbSI+U3RyZWFtIGdlc3RvcHB0PC90ZXh0Pgo8L3N2Zz4=';
            this.showNotification('📹 Stream gestoppt', 'info');
        } else {
            // Stream starten
            streamImg.src = '/api/camera/stream';
            this.showNotification('📹 Stream gestartet', 'info');
        }
    }
    
    downloadImages() {
        this.showNotification('💾 Download wird vorbereitet...', 'info');
        window.open('/api/camera/download_all', '_blank');
    }
    
    openImageModal(filename) {
        // Simple Modal - kann später erweitert werden
        window.open(`/api/camera/image/${filename}`, '_blank');
    }
    
    showNotification(message, type = 'info') {
        // Bestehende Notifications entfernen
        const existingNotifications = document.querySelectorAll('.notification');
        existingNotifications.forEach(n => n.remove());
        
        // Neue Notification erstellen
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        // Auto-Remove nach 3 Sekunden
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 3000);
        
        console.log(`${type.toUpperCase()}: ${message}`);
    }
    
    setButtonLoading(button, loading) {
        if (loading) {
            button.setAttribute('data-loading', 'true');
            button.disabled = true;
        } else {
            button.removeAttribute('data-loading');
            button.disabled = false;
        }
    }
}

// Globale Instanz erstellen
const cameraController = new CameraController();

// Globale Funktionen für onclick-Handler (Rückwärtskompatibilität)
function updateCameraStats() {
    cameraController.updateCameraStats();
}

function captureImage() {
    cameraController.captureImage();
}

function detectWeeds() {
    cameraController.detectWeeds();
}

function continuousDetection() {
    cameraController.toggleContinuousDetection();
}

function clearResults() {
    cameraController.clearResults();
}

function loadImageGallery() {
    cameraController.loadImageGallery();
}

function downloadImages() {
    cameraController.downloadImages();
}

function clearImages() {
    cameraController.clearAllImages();
}

function toggleStream() {
    cameraController.toggleStream();
}

// Cleanup bei Seitenwechsel
window.addEventListener('beforeunload', () => {
    if (statsUpdateInterval) {
        clearInterval(statsUpdateInterval);
    }
});

// console.log('📹 Clean Camera JavaScript geladen - img_ Dateinamen & Kreuz-Button!');