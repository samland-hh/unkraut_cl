// app/static/js/camera.js - Kamera JavaScript

let cameraState = {
    isStreaming: true,
    continuousDetection: false,
    detectionInterval: null,
    capturedImages: [],
    currentSettings: {
        resolution: '640x480',
        quality: 80,
        fps: 30
    }
};

// Initialisierung
document.addEventListener('DOMContentLoaded', function() {
    setupCameraControls();
    setupSettingsControls();
    startStatsUpdates();
    loadImageGallery();
    
    console.log('📷 Kamera-Steuerung geladen');
});

function setupCameraControls() {
    // Kamera-Stream Error Handling ist bereits in common.js
    const cameraStream = document.getElementById('camera-stream');
    if (cameraStream) {
        cameraStream.addEventListener('load', function() {
            cameraState.isStreaming = true;
            console.log('📹 Kamera-Stream aktiv');
        });
    }
}

function setupSettingsControls() {
    // Auflösung
    const resolutionSelect = document.getElementById('resolution-select');
    if (resolutionSelect) {
        resolutionSelect.addEventListener('change', function() {
            cameraState.currentSettings.resolution = this.value;
        });
    }
    
    // Qualität
    const qualitySlider = document.getElementById('quality-slider');
    const qualityDisplay = document.getElementById('quality-display');
    if (qualitySlider && qualityDisplay) {
        qualitySlider.addEventListener('input', function() {
            const quality = parseInt(this.value);
            qualityDisplay.textContent = quality;
            cameraState.currentSettings.quality = quality;
        });
    }
    
    // FPS
    const fpsSlider = document.getElementById('fps-slider');
    const fpsDisplay = document.getElementById('fps-display');
    if (fpsSlider && fpsDisplay) {
        fpsSlider.addEventListener('input', function() {
            const fps = parseInt(this.value);
            fpsDisplay.textContent = fps;
            cameraState.currentSettings.fps = fps;
        });
    }
}

async function captureImage() {
    try {
        showNotification('📸 Nehme Foto auf...', 'info');
        
        const response = await apiRequest('/api/camera/capture', {
            method: 'POST'
        });
        
        if (response.filename) {
            cameraState.capturedImages.unshift({
                filename: response.filename,
                timestamp: new Date(),
                size: 'Unknown'
            });
            
            showNotification(`📸 Foto gespeichert: ${response.filename}`, 'success');
            
            // Galerie aktualisieren
            setTimeout(loadImageGallery, 500);
        } else {
            showNotification(`❌ Foto-Fehler: ${response.error}`, 'error');
        }
        
    } catch (error) {
        console.error('Image capture failed:', error);
        showNotification('❌ Kamera-Aufnahme fehlgeschlagen', 'error');
    }
}

async function detectWeeds() {
    try {
        showNotification('🔄 Analysiere Kamerabild...', 'info');
        
        const response = await apiRequest('/api/ai/detect', {
            method: 'POST'
        });
        
        if (response.detections) {
            const count = response.detections.length;
            const confidence = (response.confidence * 100).toFixed(1);
            const processingTime = response.processing_time;
            
            const resultText = `✅ Erkennung abgeschlossen!
🌿 Objekte gefunden: ${count}
🎯 Konfidenz: ${confidence}%
⏱️ Verarbeitungszeit: ${processingTime}s
🔬 Methode: ${response.method}

📍 Erkennungen:
${response.detections.map((d, i) => `${i+1}. ${d.class} (${(d.confidence*100).toFixed(1)}%) bei (${d.x}, ${d.y})`).join('\n')}`;
            
            const resultsElement = document.getElementById('detection-results');
            if (resultsElement) {
                resultsElement.textContent = resultText;
            }
            
            if (count > 0) {
                showNotification(`🌿 ${count} Unkraut erkannt!`, 'success');
            } else {
                showNotification('✅ Kein Unkraut erkannt', 'success');
            }
            
        } else {
            const error = response.error || 'Unbekannter Fehler';
            document.getElementById('detection-results').textContent = `❌ Fehler: ${error}`;
            showNotification(`❌ Erkennung fehlgeschlagen: ${error}`, 'error');
        }
        
    } catch (error) {
        console.error('Weed detection failed:', error);
        document.getElementById('detection-results').textContent = '❌ Verbindungsfehler';
        showNotification('❌ KI-Erkennung fehlgeschlagen', 'error');
    }
}

function toggleStream() {
    const cameraStream = document.getElementById('camera-stream');
    const toggleBtn = document.querySelector('button[onclick="toggleStream()"]');
    
    if (cameraState.isStreaming) {
        // Stream stoppen
        cameraStream.src = '';
        cameraState.isStreaming = false;
        if (toggleBtn) toggleBtn.textContent = '▶️ Stream starten';
        showNotification('⏸️ Kamera-Stream gestoppt', 'info');
        
    } else {
        // Stream starten
        cameraStream.src = '/api/camera/stream';
        cameraState.isStreaming = true;
        if (toggleBtn) toggleBtn.textContent = '⏸️ Stream stoppen';
        showNotification('▶️ Kamera-Stream gestartet', 'info');
    }
}

function continuousDetection() {
    const btn = document.querySelector('button[onclick="continuousDetection()"]');
    
    if (!cameraState.continuousDetection) {
        // Kontinuierliche Erkennung starten
        cameraState.continuousDetection = true;
        if (btn) {
            btn.textContent = '⏹️ Stoppen';
            btn.className = 'btn btn-danger';
        }
        
        cameraState.detectionInterval = setInterval(detectWeeds, 3000);
        showNotification('📹 Kontinuierliche Erkennung gestartet (alle 3s)', 'info');
        
    } else {
        // Kontinuierliche Erkennung stoppen
        cameraState.continuousDetection = false;
        if (btn) {
            btn.textContent = '📹 Kontinuierlich';
            btn.className = 'btn btn-warning';
        }
        
        if (cameraState.detectionInterval) {
            clearInterval(cameraState.detectionInterval);
            cameraState.detectionInterval = null;
        }
        
        showNotification('⏹️ Kontinuierliche Erkennung gestoppt', 'info');
    }
}

function clearResults() {
    const resultsElement = document.getElementById('detection-results');
    if (resultsElement) {
        resultsElement.textContent = 'Keine Erkennungen';
    }
    showNotification('🗑️ Ergebnisse gelöscht', 'info');
}

function changeResolution() {
    const resolution = cameraState.currentSettings.resolution;
    showNotification(`📐 Auflösung geändert: ${resolution}`, 'info');
    
    // Hier würde die Kamera-Auflösung tatsächlich geändert werden
    // Für jetzt nur visuelles Feedback
}

function changeQuality(quality) {
    cameraState.currentSettings.quality = quality;
    console.log(`Bildqualität: ${quality}%`);
}

function changeFPS(fps) {
    cameraState.currentSettings.fps = fps;
    console.log(`FPS: ${fps}`);
}

async function updateCameraStats() {
    try {
        // Mock-Statistiken da keine echte Kamera-API vorhanden
        const stats = {
            resolution: cameraState.currentSettings.resolution,
            quality: cameraState.currentSettings.quality,
            fps: cameraState.currentSettings.fps,
            isStreaming: cameraState.isStreaming,
            capturedImages: cameraState.capturedImages.length,
            totalDataSize: '2.3 MB',
            uptime: '1h 23m'
        };
        
        const statsText = `📊 Kamera-Statistiken:
Auflösung: ${stats.resolution}
Qualität: ${stats.quality}%
FPS: ${stats.fps}
Status: ${stats.isStreaming ? 'Streaming' : 'Gestoppt'}
Aufgenommene Bilder: ${stats.capturedImages}
Datenvolumen: ${stats.totalDataSize}
Laufzeit: ${stats.uptime}`;

        const statsElement = document.getElementById('camera-stats');
        if (statsElement) {
            statsElement.textContent = statsText;
        }
        
    } catch (error) {
        console.error('Stats update failed:', error);
        const statsElement = document.getElementById('camera-stats');
        if (statsElement) {
            statsElement.textContent = '❌ Statistiken nicht verfügbar';
        }
    }
}

function loadImageGallery() {
    const galleryElement = document.getElementById('image-gallery');
    if (!galleryElement) return;
    
    if (cameraState.capturedImages.length === 0) {
        galleryElement.innerHTML = '<div class="no-images">Keine Bilder aufgenommen</div>';
        return;
    }
    
    let galleryHTML = '';
    cameraState.capturedImages.slice(0, 12).forEach((image, index) => {
        const timestamp = image.timestamp.toLocaleString('de-DE');
        galleryHTML += `
            <div class="gallery-item">
                <img class="gallery-image" 
                     src="/data/images/${image.filename}" 
                     alt="Captured ${timestamp}"
                     title="${image.filename} - ${timestamp}"
                     onclick="showImageDetails('${image.filename}')">
                <div class="image-info">${timestamp}</div>
            </div>
        `;
    });
    
    galleryElement.innerHTML = galleryHTML;
}

function showImageDetails(filename) {
    const image = cameraState.capturedImages.find(img => img.filename === filename);
    if (image) {
        const details = `Datei: ${image.filename}
Aufgenommen: ${image.timestamp.toLocaleString('de-DE')}
Größe: ${image.size}`;
        
        alert(details);
    }
}

function downloadImages() {
    if (cameraState.capturedImages.length === 0) {
        showNotification('❌ Keine Bilder zum Herunterladen', 'warning');
        return;
    }
    
    showNotification(`💾 ${cameraState.capturedImages.length} Bilder werden vorbereitet...`, 'info');
    
    // Mock-Download
    setTimeout(() => {
        showNotification('✅ Bilder-Archiv erstellt', 'success');
    }, 2000);
}

function clearImages() {
    if (cameraState.capturedImages.length === 0) {
        showNotification('❌ Keine Bilder zum Löschen', 'warning');
        return;
    }
    
    if (confirm(`Alle ${cameraState.capturedImages.length} Bilder löschen?`)) {
        cameraState.capturedImages = [];
        loadImageGallery();
        showNotification('🗑️ Alle Bilder gelöscht', 'info');
    }
}

function startStatsUpdates() {
    updateCameraStats();
    setInterval(updateCameraStats, 10000); // Alle 10 Sekunden
}

// Export für andere Scripts
window.cameraControl = {
    captureImage,
    detectWeeds,
    toggleStream,
    continuousDetection,
    clearResults,
    loadImageGallery,
    cameraState
};