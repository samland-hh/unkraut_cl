// app/static/js/camera.js
/**
 * Unkraut-2025 Kamera-Steuerung mit korrigierten API-Endpoints
 * Repariert die 404-Fehler bei Gallery und Stats
 */

class CameraController {
    constructor() {
        this.isCapturing = false;
        this.isDetecting = false;
        this.isStreaming = false;
        this.autoRefreshInterval = null;
        this.cameraSettings = {
            resolution: '640x480',
            quality: 85,
            awb_mode: 'auto',
            shutter_speed: 'auto'
        };
        
        console.log('📷 Camera Controller initialisiert');
        this.init();
    }
    
    init() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupEventListeners());
        } else {
            this.setupEventListeners();
        }
        
        // Initial laden
        this.updateStatus();
        this.loadGallery();
        this.startAutoRefresh();
    }
    
    setupEventListeners() {
        // Capture Button
        const captureBtn = document.getElementById('capture-btn') || 
                          document.querySelector('[data-action="capture"]') ||
                          document.querySelector('.btn[onclick*="capture"]');
        
        if (captureBtn) {
            captureBtn.removeAttribute('onclick'); // Entferne alte onclick
            captureBtn.addEventListener('click', () => this.captureImage());
            console.log('📸 Capture Button verbunden');
        }
        
        // Detection Button
        const detectBtn = document.getElementById('detect-btn') || 
                         document.querySelector('[data-action="detect"]');
        
        if (detectBtn) {
            detectBtn.addEventListener('click', () => this.runDetection());
            console.log('🔍 Detection Button verbunden');
        }
        
        // Gallery Buttons
        this.bindGalleryButtons();
        
        // Settings
        this.bindSettingsControls();
        
        console.log('✅ Event Listeners verbunden');
    }
    
    bindGalleryButtons() {
        // Load Gallery Button
        const loadBtn = document.querySelector('[data-gallery-action="load"]') ||
                       document.querySelector('.btn[onclick*="loadGallery"]');
        if (loadBtn) {
            loadBtn.removeAttribute('onclick');
            loadBtn.addEventListener('click', () => this.loadGallery());
        }
        
        // Download Button
        const downloadBtn = document.querySelector('[data-gallery-action="download"]') ||
                           document.querySelector('.btn[onclick*="downloadImages"]');
        if (downloadBtn) {
            downloadBtn.removeAttribute('onclick');
            downloadBtn.addEventListener('click', () => this.downloadImages());
        }
        
        // Clear Button
        const clearBtn = document.querySelector('[data-gallery-action="clear"]') ||
                        document.querySelector('.btn[onclick*="clearImages"]');
        if (clearBtn) {
            clearBtn.removeAttribute('onclick');
            clearBtn.addEventListener('click', () => this.clearGallery());
        }
    }
    
    bindSettingsControls() {
        const settingsControls = document.querySelectorAll('[data-setting]');
        settingsControls.forEach(control => {
            const setting = control.dataset.setting;
            control.addEventListener('change', (e) => {
                this.cameraSettings[setting] = e.target.value;
                console.log(`⚙️ Setting changed: ${setting} = ${e.target.value}`);
            });
        });
    }
    
    async captureImage() {
        if (this.isCapturing) {
            console.log('⏳ Capture läuft bereits...');
            return;
        }
        
        this.isCapturing = true;
        this.updateCaptureButton('🔄 Aufnehmen...');
        
        try {
            console.log('📸 Starte Capture...');
            
            const response = await fetch('/api/camera/capture', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(this.cameraSettings)
            });
            
            const result = await response.json();
            
            if (response.ok) {
                console.log('✅ Capture erfolgreich:', result);
                this.showNotification(`✅ Foto gespeichert: ${result.filename}`, 'success');
                
                // Galerie nach kurzer Pause aktualisieren
                setTimeout(() => this.loadGallery(), 1500);
                
                // Custom Event für andere Scripts
                document.dispatchEvent(new CustomEvent('imageCapture', { 
                    detail: result 
                }));
                
            } else {
                throw new Error(result.error || 'Capture fehlgeschlagen');
            }
            
        } catch (error) {
            console.error('❌ Capture-Fehler:', error);
            this.showNotification(`❌ Capture fehlgeschlagen: ${error.message}`, 'error');
        } finally {
            this.isCapturing = false;
            this.updateCaptureButton('📸 Foto aufnehmen');
        }
    }
    
    async runDetection() {
        if (this.isDetecting) {
            console.log('⏳ Detection läuft bereits...');
            return;
        }
        
        this.isDetecting = true;
        this.updateDetectionButton('🔄 Analysiere...');
        this.updateDetectionResults('🔍 Starte Unkraut-Erkennung...\n⏳ Bitte warten...');
        
        try {
            console.log('🔍 Starte Unkraut-Erkennung...');
            
            const response = await fetch('/api/ai/detect', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(this.cameraSettings)
            });
            
            const result = await response.json();
            
            if (response.ok) {
                console.log('✅ Detection erfolgreich:', result);
                this.displayDetectionResults(result);
                this.showNotification(`✅ ${result.detections?.length || 0} Unkräuter erkannt`, 'success');
            } else {
                throw new Error(result.error || 'Detection fehlgeschlagen');
            }
            
        } catch (error) {
            console.error('❌ Detection-Fehler:', error);
            this.updateDetectionResults(`❌ Fehler bei der Unkraut-Erkennung:\n${error.message}`);
            this.showNotification(`❌ Detection fehlgeschlagen: ${error.message}`, 'error');
        } finally {
            this.isDetecting = false;
            this.updateDetectionButton('🔍 Unkraut erkennen');
        }
    }
    
    async loadGallery() {
        try {
            console.log('📸 Lade Bildergalerie...');
            
            // ✅ KORRIGIERTER ENDPOINT
            const response = await fetch('/api/gallery/images');
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            console.log(`📊 Galerie geladen: ${data.count} Bilder`);
            
            this.renderGallery(data.images || []);
            
        } catch (error) {
            console.error('❌ Gallery-Load-Fehler:', error);
            this.renderGalleryError(error.message);
        }
    }
    
    renderGallery(images) {
        const container = document.getElementById('image-gallery') || 
                         document.querySelector('.image-gallery');
        
        if (!container) {
            console.warn('❌ Gallery-Container nicht gefunden');
            return;
        }
        
        if (images.length === 0) {
            container.innerHTML = `
                <div class="gallery-empty">
                    <p>📭 Noch keine Bilder aufgenommen</p>
                    <p>Nutze den "📸 Foto aufnehmen" Button</p>
                </div>
            `;
            return;
        }
        
        let html = `
            <div class="gallery-header">
                <p><strong>${images.length} Bilder</strong></p>
            </div>
            <div class="gallery-grid">
        `;
        
        images.forEach(image => {
            html += `
                <div class="gallery-item" data-filename="${image.filename}">
                    <img src="/api/gallery/image/${image.filename}" 
                         class="gallery-image" 
                         alt="${image.filename}"
                         loading="lazy"
                         onclick="cameraController.showImageModal('${image.filename}')"
                         onerror="this.src='data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgZmlsbD0iIzMzMyIvPjx0ZXh0IHg9IjUwIiB5PSI1NSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZmlsbD0iI2ZmZiI+4p2MPC90ZXh0Pjwvc3ZnPg=='">
                    <div class="image-info">
                        <div class="image-name">${image.filename}</div>
                        <div class="image-size">${this.formatFileSize(image.size)}</div>
                        <button class="btn-small btn-danger" 
                                onclick="cameraController.deleteImage('${image.filename}')">
                            🗑️ Löschen
                        </button>
                    </div>
                </div>
            `;
        });
        
        html += '</div>';
        container.innerHTML = html;
        
        console.log(`✅ Galerie gerendert: ${images.length} Bilder`);
    }
    
    renderGalleryError(errorMessage) {
        const container = document.getElementById('image-gallery') || 
                         document.querySelector('.image-gallery');
        
        if (container) {
            container.innerHTML = `
                <div class="gallery-error">
                    <p>❌ Fehler beim Laden der Galerie</p>
                    <p><small>${errorMessage}</small></p>
                    <button class="btn btn-info" onclick="cameraController.loadGallery()">
                        🔄 Erneut versuchen
                    </button>
                </div>
            `;
        }
    }
    
    async deleteImage(filename) {
        if (!confirm(`🗑️ Bild "${filename}" wirklich löschen?`)) {
            return;
        }
        
        try {
            console.log(`🗑️ Lösche Bild: ${filename}`);
            
            const response = await fetch(`/api/gallery/delete/${filename}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                console.log(`✅ Bild gelöscht: ${filename}`);
                this.showNotification(`✅ Bild "${filename}" gelöscht`, 'success');
                this.loadGallery(); // Galerie neu laden
            } else {
                throw new Error(`Löschen fehlgeschlagen: ${response.status}`);
            }
            
        } catch (error) {
            console.error('❌ Delete-Fehler:', error);
            this.showNotification(`❌ Löschen fehlgeschlagen: ${error.message}`, 'error');
        }
    }
    
    async downloadImages() {
        try {
            console.log('💾 Starte Download...');
            
            const response = await fetch('/api/gallery/download', {
                method: 'POST'
            });
            
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `unkraut_bilder_${Date.now()}.zip`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
                
                this.showNotification('✅ Download gestartet!', 'success');
            } else {
                throw new Error(`Download fehlgeschlagen: ${response.status}`);
            }
            
        } catch (error) {
            console.error('❌ Download-Fehler:', error);
            this.showNotification(`❌ Download fehlgeschlagen: ${error.message}`, 'error');
        }
    }
    
    async clearGallery() {
        if (!confirm('🗑️ ALLE Bilder löschen?\n\nDieser Vorgang kann nicht rückgängig gemacht werden!')) {
            return;
        }
        
        try {
            console.log('🗑️ Lösche alle Bilder...');
            
            const response = await fetch('/api/gallery/clear', {
                method: 'POST'
            });
            
            if (response.ok) {
                const result = await response.json();
                console.log('✅ Galerie geleert:', result);
                this.showNotification(`✅ ${result.deleted} Bilder gelöscht`, 'success');
                this.loadGallery(); // Galerie neu laden
            } else {
                throw new Error(`Löschen fehlgeschlagen: ${response.status}`);
            }
            
        } catch (error) {
            console.error('❌ Clear-Fehler:', error);
            this.showNotification(`❌ Löschen fehlgeschlagen: ${error.message}`, 'error');
        }
    }
    
    async updateStatus() {
        try {
            // ✅ KORRIGIERTER ENDPOINT  
            const response = await fetch('/api/system/status');
            
            if (response.ok) {
                const status = await response.json();
                this.displayStatus(status);
            } else {
                throw new Error(`Status-API Fehler: ${response.status}`);
            }
            
        } catch (error) {
            console.warn('⚠️ Status-Update-Fehler:', error);
            this.displayStatus({
                error: error.message,
                timestamp: Date.now(),
                system: { error: 'Status nicht verfügbar' }
            });
        }
    }
    
    displayStatus(status) {
        const statusElement = document.getElementById('camera-status') || 
                             document.querySelector('.status-display');
        
        if (!statusElement) return;
        
        if (status.error) {
            statusElement.textContent = `❌ Status-Fehler: ${status.error}`;
            return;
        }
        
        const systemInfo = status.system || {};
        const hardwareInfo = status.hardware || {};
        
        let statusText = `📷 Kamera-Status (${new Date(status.timestamp * 1000).toLocaleTimeString()})\n\n`;
        
        // System-Info
        if (systemInfo.cpu_usage !== undefined) {
            statusText += `💻 CPU: ${systemInfo.cpu_usage.toFixed(1)}%\n`;
        }
        if (systemInfo.memory_usage !== undefined) {
            statusText += `🧠 RAM: ${systemInfo.memory_usage.toFixed(1)}%\n`;
        }
        if (systemInfo.temperature !== undefined) {
            statusText += `🌡️ Temp: ${systemInfo.temperature.toFixed(1)}°C\n`;
        }
        
        // Hardware-Info
        statusText += `\n📷 Kamera: ${hardwareInfo.camera_available ? '✅ Verfügbar' : '❌ Nicht verfügbar'}\n`;
        statusText += `🦾 Roboterarm: ${hardwareInfo.arm_available ? '✅ Verfügbar' : '❌ Nicht verfügbar'}\n`;
        statusText += `🧠 KI: ${hardwareInfo.ai_available ? '✅ Verfügbar' : '❌ Nicht verfügbar'}\n`;
        
        statusElement.textContent = statusText;
    }
    
    displayDetectionResults(result) {
        const resultsElement = document.getElementById('detection-results') || 
                              document.querySelector('.detection-results');
        
        if (!resultsElement) return;
        
        let resultsText = `🔍 Unkraut-Erkennungs-Ergebnisse\n`;
        resultsText += `⏰ ${new Date().toLocaleTimeString()}\n\n`;
        
        if (result.detections && result.detections.length > 0) {
            resultsText += `✅ ${result.detections.length} Unkräuter erkannt:\n\n`;
            
            result.detections.forEach((detection, i) => {
                resultsText += `${i + 1}. ${detection.class || 'Unkraut'}\n`;
                resultsText += `   Konfidenz: ${(detection.confidence * 100).toFixed(1)}%\n`;
                if (detection.bbox) {
                    resultsText += `   Position: (${detection.bbox.x}, ${detection.bbox.y})\n`;
                }
                resultsText += `\n`;
            });
        } else {
            resultsText += `✅ Keine Unkräuter erkannt\n`;
            resultsText += `🌱 Bereich ist sauber!`;
        }
        
        resultsElement.textContent = resultsText;
        resultsElement.className = result.detections?.length > 0 ? 
            'detection-results has-results' : 'detection-results';
    }
    
    showImageModal(filename) {
        const imageUrl = `/api/gallery/image/${filename}`;
        
        const modal = document.createElement('div');
        modal.style.cssText = `
            position: fixed; top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0,0,0,0.8); z-index: 9999;
            display: flex; align-items: center; justify-content: center;
            cursor: pointer;
        `;
        
        modal.innerHTML = `
            <div style="max-width: 90%; max-height: 90%; text-align: center;">
                <img src="${imageUrl}" style="max-width: 100%; max-height: 100%; border-radius: 8px;">
                <p style="color: white; margin-top: 10px;">${filename}</p>
            </div>
        `;
        
        modal.onclick = () => document.body.removeChild(modal);
        document.body.appendChild(modal);
    }
    
    startAutoRefresh() {
        // Status alle 30 Sekunden aktualisieren
        this.autoRefreshInterval = setInterval(() => {
            this.updateStatus();
        }, 30000);
        
        console.log('🔄 Auto-Refresh gestartet');
    }
    
    updateCaptureButton(text) {
        const btn = document.getElementById('capture-btn') || 
                   document.querySelector('[data-action="capture"]');
        if (btn) {
            btn.textContent = text;
            btn.disabled = this.isCapturing;
        }
    }
    
    updateDetectionButton(text) {
        const btn = document.getElementById('detect-btn') || 
                   document.querySelector('[data-action="detect"]');
        if (btn) {
            btn.textContent = text;
            btn.disabled = this.isDetecting;
        }
    }
    
    updateDetectionResults(text) {
        const element = document.getElementById('detection-results') || 
                       document.querySelector('.detection-results');
        if (element) {
            element.textContent = text;
        }
    }
    
    showNotification(message, type = 'info') {
        console.log(`${type.toUpperCase()}: ${message}`);
        
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed; top: 20px; right: 20px; z-index: 8888;
            padding: 12px 20px; border-radius: 6px; color: white;
            background: ${type === 'error' ? '#f44336' : type === 'warning' ? '#ff9800' : type === 'success' ? '#4caf50' : '#2196f3'};
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            max-width: 300px; font-size: 14px;
        `;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            if (document.body.contains(notification)) {
                document.body.removeChild(notification);
            }
        }, 5000);
    }
    
    formatFileSize(bytes) {
        if (!bytes) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }
    
    // Cleanup bei Page-Unload
    destroy() {
        if (this.autoRefreshInterval) {
            clearInterval(this.autoRefreshInterval);
        }
    }
}

// Globale Instanz erstellen
console.log('🚀 Initialisiere korrigierten Camera Controller...');
window.cameraController = new CameraController();

// Cleanup bei Page-Unload
window.addEventListener('beforeunload', () => {
    if (window.cameraController) {
        window.cameraController.destroy();
    }
});

// Legacy-Funktionen für Kompatibilität
window.captureImage = () => window.cameraController.captureImage();
window.runDetection = () => window.cameraController.runDetection();
window.loadGallery = () => window.cameraController.loadGallery();
window.downloadImages = () => window.cameraController.downloadImages();
window.clearImages = () => window.cameraController.clearGallery();

console.log('✅ Korrigierte Camera Controller geladen - API-Endpoints repariert!');