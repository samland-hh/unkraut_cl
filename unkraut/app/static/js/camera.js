// app/static/js/camera.js - Saubere HTML/CSS/JS Trennung
/**
 * Kamera-Steuerung für Unkraut-2025
 * Bindet sich automatisch an DOM-Elemente über data-Attribute
 */

class CameraController {
    constructor() {
        this.state = {
            isStreaming: true,
            continuousDetection: false,
            detectionInterval: null,
            currentSettings: {
                resolution: '640x480',
                quality: 80,
                fps: 30
            }
        };
        
        // Automatische Initialisierung
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.init());
        } else {
            this.init();
        }
    }
    
    init() {
        console.log('📷 Initialisiere Kamera-Controller...');
        
        // Event-Listener binden
        this.bindEventListeners();
        
        // Kamera-Stream Setup
        this.setupCameraStream();
        
        // Einstellungen laden
        this.loadSettings();
        
        // Statistiken starten
        this.startStatsUpdates();
        
        console.log('✅ Kamera-Controller bereit');
    }
    
    bindEventListeners() {
        // Kamera-Aktionen
        document.querySelectorAll('[data-camera-action]').forEach(btn => {
            const action = btn.dataset.cameraAction;
            btn.addEventListener('click', (e) => this.handleCameraAction(action, e));
        });
        
        // AI-Aktionen
        document.querySelectorAll('[data-ai-action]').forEach(btn => {
            const action = btn.dataset.aiAction;
            btn.addEventListener('click', (e) => this.handleAIAction(action, e));
        });
        
        // Statistik-Aktionen
        document.querySelectorAll('[data-stats-action]').forEach(btn => {
            const action = btn.dataset.statsAction;
            btn.addEventListener('click', (e) => this.handleStatsAction(action, e));
        });
        
        // Einstellungen
        document.querySelectorAll('[data-setting]').forEach(element => {
            const setting = element.dataset.setting;
            element.addEventListener('change', (e) => this.handleSettingChange(setting, e));
            element.addEventListener('input', (e) => this.handleSettingInput(setting, e));
        });
        
        console.log('📎 Event-Listener gebunden');
    }
    
    setupCameraStream() {
        const streamImg = document.getElementById('camera-stream');
        if (streamImg) {
            streamImg.addEventListener('load', () => {
                this.state.isStreaming = true;
                console.log('📹 Kamera-Stream aktiv');
            });
            
            streamImg.addEventListener('error', () => {
                console.warn('❌ Kamera-Stream Fehler');
                this.state.isStreaming = false;
            });
        }
    }
    
    loadSettings() {
        // Einstellungen aus localStorage laden (falls vorhanden)
        const savedSettings = localStorage.getItem('cameraSettings');
        if (savedSettings) {
            try {
                this.state.currentSettings = {...this.state.currentSettings, ...JSON.parse(savedSettings)};
                this.applySettings();
            } catch (e) {
                console.warn('Gespeicherte Einstellungen konnten nicht geladen werden');
            }
        }
    }
    
    applySettings() {
        // Einstellungen in UI anwenden
        const resolutionSelect = document.getElementById('resolution-select');
        if (resolutionSelect) {
            resolutionSelect.value = this.state.currentSettings.resolution;
        }
        
        const qualitySlider = document.getElementById('quality-slider');
        const qualityDisplay = document.getElementById('quality-display');
        if (qualitySlider && qualityDisplay) {
            qualitySlider.value = this.state.currentSettings.quality;
            qualityDisplay.textContent = this.state.currentSettings.quality;
        }
        
        const fpsSlider = document.getElementById('fps-slider');
        const fpsDisplay = document.getElementById('fps-display');
        if (fpsSlider && fpsDisplay) {
            fpsSlider.value = this.state.currentSettings.fps;
            fpsDisplay.textContent = this.state.currentSettings.fps;
        }
    }
    
    saveSettings() {
        localStorage.setItem('cameraSettings', JSON.stringify(this.state.currentSettings));
    }
    
    async handleCameraAction(action, event) {
        const button = event.target;
        this.setButtonLoading(button, true);
        
        try {
            switch(action) {
                case 'capture':
                    await this.captureImage();
                    break;
                case 'detect':
                    await this.detectWeeds();
                    break;
                case 'toggle-stream':
                    this.toggleStream();
                    break;
                default:
                    console.warn(`Unbekannte Kamera-Aktion: ${action}`);
            }
        } catch (error) {
            console.error(`Fehler bei Kamera-Aktion ${action}:`, error);
            this.showNotification(`❌ Fehler: ${error.message}`, 'error');
        } finally {
            this.setButtonLoading(button, false);
        }
    }
    
    async handleAIAction(action, event) {
        const button = event.target;
        this.setButtonLoading(button, true);
        
        try {
            switch(action) {
                case 'detect':
                    await this.detectWeeds();
                    break;
                case 'continuous':
                    this.toggleContinuousDetection();
                    break;
                case 'clear':
                    this.clearDetectionResults();
                    break;
                default:
                    console.warn(`Unbekannte AI-Aktion: ${action}`);
            }
        } catch (error) {
            console.error(`Fehler bei AI-Aktion ${action}:`, error);
            this.showNotification(`❌ Fehler: ${error.message}`, 'error');
        } finally {
            this.setButtonLoading(button, false);
        }
    }
    
    async handleStatsAction(action, event) {
        const button = event.target;
        this.setButtonLoading(button, true);
        
        try {
            switch(action) {
                case 'update':
                    await this.updateCameraStats();
                    break;
                default:
                    console.warn(`Unbekannte Stats-Aktion: ${action}`);
            }
        } catch (error) {
            console.error(`Fehler bei Stats-Aktion ${action}:`, error);
        } finally {
            this.setButtonLoading(button, false);
        }
    }
    
    handleSettingChange(setting, event) {
        const value = event.target.value;
        this.state.currentSettings[setting] = value;
        this.saveSettings();
        console.log(`⚙️ Einstellung geändert: ${setting} = ${value}`);
    }
    
    handleSettingInput(setting, event) {
        const value = event.target.value;
        this.state.currentSettings[setting] = parseInt(value) || value;
        
        // Display-Updates für Slider
        if (setting === 'quality') {
            const display = document.getElementById('quality-display');
            if (display) display.textContent = value;
        } else if (setting === 'fps') {
            const display = document.getElementById('fps-display');
            if (display) display.textContent = value;
        }
    }
    
    async captureImage() {
        try {
            this.showNotification('📸 Nehme Foto auf...', 'info');
            
            const response = await fetch('/api/camera/capture', {
                method: 'POST'
            });
            
            const result = await response.json();
            
            if (result.filename) {
                this.showNotification(`📸 Foto gespeichert: ${result.filename}`, 'success');
                
                // Event für andere Module (z.B. Galerie)
                document.dispatchEvent(new CustomEvent('imageCapture', {
                    detail: { filename: result.filename }
                }));
                
                return result;
            } else {
                throw new Error(result.error || 'Capture fehlgeschlagen');
            }
            
        } catch (error) {
            console.error('Capture-Fehler:', error);
            this.showNotification(`❌ Foto-Aufnahme fehlgeschlagen: ${error.message}`, 'error');
            throw error;
        }
    }
    
    async detectWeeds() {
        try {
            this.showNotification('🔄 Analysiere Kamerabild...', 'info');
            
            const response = await fetch('/api/ai/detect', {
                method: 'POST'
            });
            
            const result = await response.json();
            
            if (result.detections) {
                const count = result.detections.length;
                const confidence = (result.confidence * 100).toFixed(1);
                
                this.showNotification(`🔍 ${count} Unkraut erkannt (${confidence}% Konfidenz)`, 'success');
                this.displayDetectionResults(result);
                
                return result;
            } else {
                throw new Error(result.error || 'Erkennung fehlgeschlagen');
            }
            
        } catch (error) {
            console.error('Detection-Fehler:', error);
            this.showNotification(`❌ Unkraut-Erkennung fehlgeschlagen: ${error.message}`, 'error');
            this.displayDetectionError(error.message);
            throw error;
        }
    }
    
    displayDetectionResults(result) {
        const container = document.getElementById('detection-results');
        if (!container) return;
        
        const count = result.detections.length;
        const confidence = (result.confidence * 100).toFixed(1);
        const processingTime = result.processing_time || 'Unbekannt';
        
        let html = `
            <div class="detection-summary">
                <h4>🔍 Erkennungsergebnis</h4>
                <p><strong>Objekte gefunden:</strong> ${count}</p>
                <p><strong>Durchschnittliche Konfidenz:</strong> ${confidence}%</p>
                <p><strong>Verarbeitungszeit:</strong> ${processingTime}s</p>
            </div>
        `;
        
        if (result.detections.length > 0) {
            html += `<div class="detection-list">`;
            result.detections.forEach((detection, index) => {
                const conf = (detection.confidence * 100).toFixed(1);
                html += `
                    <div class="detection-item">
                        <span>🌿 ${index + 1}. ${detection.class || 'Unkraut'}</span>
                        <span>${conf}%</span>
                        <span>(${detection.x}, ${detection.y})</span>
                    </div>
                `;
            });
            html += `</div>`;
        }
        
        container.innerHTML = html;
        container.className = 'detection-results has-results';
    }
    
    displayDetectionError(message) {
        const container = document.getElementById('detection-results');
        if (!container) return;
        
        container.innerHTML = `
            <div class="detection-error">
                <h4>❌ Erkennungsfehler</h4>
                <p>${message}</p>
            </div>
        `;
        container.className = 'detection-results has-error';
    }
    
    clearDetectionResults() {
        const container = document.getElementById('detection-results');
        if (container) {
            container.innerHTML = '<p>Keine Erkennung durchgeführt</p>';
            container.className = 'detection-results';
        }
        this.showNotification('🧹 Erkennungsergebnisse gelöscht', 'info');
    }
    
    toggleStream() {
        // Toggle-Logik für Stream
        const streamImg = document.getElementById('camera-stream');
        if (!streamImg) return;
        
        if (this.state.isStreaming) {
            streamImg.style.display = 'none';
            this.state.isStreaming = false;
            this.showNotification('⏸️ Stream pausiert', 'info');
        } else {
            streamImg.style.display = 'block';
            this.state.isStreaming = true;
            this.showNotification('▶️ Stream gestartet', 'info');
        }
    }
    
    toggleContinuousDetection() {
        if (this.state.continuousDetection) {
            // Stoppe kontinuierliche Erkennung
            if (this.state.detectionInterval) {
                clearInterval(this.state.detectionInterval);
                this.state.detectionInterval = null;
            }
            this.state.continuousDetection = false;
            this.showNotification('⏹️ Kontinuierliche Erkennung gestoppt', 'info');
            
            // Button-Text zurücksetzen
            const button = document.querySelector('[data-ai-action="continuous"]');
            if (button) button.textContent = '🔄 Kontinuierliche Erkennung';
            
        } else {
            // Starte kontinuierliche Erkennung
            this.state.continuousDetection = true;
            this.state.detectionInterval = setInterval(() => {
                this.detectWeeds().catch(console.error);
            }, 5000); // Alle 5 Sekunden
            
            this.showNotification('🔄 Kontinuierliche Erkennung gestartet', 'success');
            
            // Button-Text ändern
            const button = document.querySelector('[data-ai-action="continuous"]');
            if (button) button.textContent = '⏹️ Erkennung stoppen';
        }
    }
    
    async updateCameraStats() {
        try {
            // Mock-Statistiken (später durch echte API ersetzen)
            const stats = {
                resolution: this.state.currentSettings.resolution,
                quality: this.state.currentSettings.quality,
                fps: this.state.currentSettings.fps,
                streaming: this.state.isStreaming,
                uptime: Math.floor(performance.now() / 1000),
                totalCaptures: localStorage.getItem('totalCaptures') || 0
            };
            
            const statsText = `
Auflösung: ${stats.resolution}
Qualität: ${stats.quality}%
FPS: ${stats.fps}
Status: ${stats.streaming ? 'Streaming' : 'Gestoppt'}
Laufzeit: ${stats.uptime}s
Aufnahmen: ${stats.totalCaptures}
            `.trim();
            
            const container = document.getElementById('camera-stats');
            if (container) {
                container.textContent = statsText;
            }
            
            console.log('📊 Kamera-Statistiken aktualisiert');
            
        } catch (error) {
            console.error('Stats-Update-Fehler:', error);
            const container = document.getElementById('camera-stats');
            if (container) {
                container.textContent = '❌ Statistiken nicht verfügbar';
            }
        }
    }
    
    startStatsUpdates() {
        // Initiales Update
        this.updateCameraStats();
        
        // Auto-Update alle 10 Sekunden
        setInterval(() => {
            this.updateCameraStats();
        }, 10000);
    }
    
    setButtonLoading(button, loading) {
        if (loading) {
            button.dataset.loading = 'true';
            button.disabled = true;
        } else {
            delete button.dataset.loading;
            button.disabled = false;
        }
    }
    
    showNotification(message, type = 'info') {
        // Nutze globale Notification-Funktion falls verfügbar
        if (window.showNotification) {
            window.showNotification(message, type);
        } else {
            // Fallback
            console.log(`${type.toUpperCase()}: ${message}`);
        }
    }
}

// Automatische Initialisierung
const cameraController = new CameraController();

// Für Debugging und externe Zugriffe
window.cameraController = cameraController;

// Globale Funktionen für Rückwärtskompatibilität (falls nötig)
window.captureImage = () => cameraController.captureImage();
window.detectWeeds = () => cameraController.detectWeeds();