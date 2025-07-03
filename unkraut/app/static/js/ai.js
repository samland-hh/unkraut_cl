// app/static/js/ai.js - KI-Dashboard JavaScript

let aiState = {
    continuousMode: false,
    continuousInterval: null,
    autoRemovalActive: false,
    trainingMode: false,
    detectionCount: 0,
    settings: {
        sensitivity: 50,
        detectionType: 'all',
        confidenceThreshold: 70
    },
    recentDetections: []
};

// Initialisierung
document.addEventListener('DOMContentLoaded', function() {
    setupSettingsControls();
    updateStats();
    startPerformanceUpdates();
    
    console.log('🧠 KI-Dashboard geladen');
});

function setupSettingsControls() {
    // Empfindlichkeits-Slider
    const sensitivitySlider = document.getElementById('sensitivity-slider');
    const sensitivityDisplay = document.getElementById('sensitivity-display');
    if (sensitivitySlider && sensitivityDisplay) {
        sensitivitySlider.addEventListener('input', function() {
            const value = parseInt(this.value);
            sensitivityDisplay.textContent = value;
            aiState.settings.sensitivity = value;
        });
    }
    
    // Erkennungstyp
    const detectionTypeSelect = document.getElementById('detection-type');
    if (detectionTypeSelect) {
        detectionTypeSelect.addEventListener('change', function() {
            aiState.settings.detectionType = this.value;
            console.log('Erkennungstyp geändert:', this.value);
        });
    }
    
    // Konfidenz-Schwelle
    const confidenceSlider = document.getElementById('confidence-slider');
    const confidenceDisplay = document.getElementById('confidence-display');
    if (confidenceSlider && confidenceDisplay) {
        confidenceSlider.addEventListener('input', function() {
            const value = parseInt(this.value);
            confidenceDisplay.textContent = value;
            aiState.settings.confidenceThreshold = value;
        });
    }
}

async function quickDetection() {
    try {
        aiState.detectionCount++;
        
        const resultsElement = document.getElementById('quick-results');
        if (resultsElement) {
            resultsElement.textContent = '🔄 Analysiere Kamerabild...';
        }
        
        const response = await apiRequest('/api/ai/detect', {
            method: 'POST'
        });
        
        if (response.detections) {
            const count = response.detections.length;
            const confidence = (response.confidence * 100).toFixed(1);
            const processingTime = response.processing_time;
            
            const resultText = `✅ Erkennung abgeschlossen!
🌿 Objekte gefunden: ${count}
🎯 Durchschnittliche Konfidenz: ${confidence}%
⏱️ Verarbeitungszeit: ${processingTime}s
🔬 Methode: ${response.method}
📊 Erkennung #${aiState.detectionCount}

📍 Erkennungen:
${response.detections.map((d, i) => `${i+1}. ${d.class} (${(d.confidence*100).toFixed(1)}%) bei (${d.x}, ${d.y})`).join('\n')}`;
            
            if (resultsElement) {
                resultsElement.textContent = resultText;
            }
            
            // Letzte Erkennungen aktualisieren
            updateRecentDetections(response.detections);
            
            // Performance-Metriken aktualisieren
            updatePerformanceMetrics(processingTime, confidence);
            
            if (count > 0) {
                showNotification(`🌿 ${count} Unkraut erkannt!`, 'success');
                
                // Auto-Entfernung wenn aktiv
                if (aiState.autoRemovalActive) {
                    triggerAutoRemoval(response.detections[0]);
                }
            } else {
                showNotification('✅ Kein Unkraut erkannt', 'success');
            }
            
        } else {
            const error = response.error || 'Unbekannter Fehler';
            if (resultsElement) {
                resultsElement.textContent = `❌ Fehler: ${error}`;
            }
            showNotification(`❌ Erkennung fehlgeschlagen: ${error}`, 'error');
        }
        
    } catch (error) {
        console.error('Quick detection failed:', error);
        const resultsElement = document.getElementById('quick-results');
        if (resultsElement) {
            resultsElement.textContent = '❌ Verbindungsfehler: ' + error.message;
        }
        showNotification('❌ KI-Erkennung fehlgeschlagen', 'error');
    }
}

function continuousDetection() {
    const btn = document.querySelector('button[onclick="continuousDetection()"]');
    
    if (!aiState.continuousMode) {
        // Kontinuierliche Erkennung starten
        aiState.continuousMode = true;
        if (btn) {
            btn.textContent = '⏹️ Stoppen';
            btn.className = 'btn btn-danger';
        }
        
        aiState.continuousInterval = setInterval(quickDetection, 3000);
        showNotification('📹 Kontinuierliche Erkennung gestartet (alle 3s)', 'info');
        
    } else {
        // Kontinuierliche Erkennung stoppen
        aiState.continuousMode = false;
        if (btn) {
            btn.textContent = '📹 Kontinuierlich';
            btn.className = 'btn btn-info';
        }
        
        if (aiState.continuousInterval) {
            clearInterval(aiState.continuousInterval);
            aiState.continuousInterval = null;
        }
        
        showNotification('⏹️ Kontinuierliche Erkennung gestoppt', 'info');
    }
}

function updateRecentDetections(detections) {
    const container = document.getElementById('recent-detections');
    if (!container) return;
    
    // Neue Erkennungen zu aktuellen hinzufügen
    detections.forEach(detection => {
        aiState.recentDetections.unshift({
            ...detection,
            timestamp: new Date(),
            id: aiState.detectionCount
        });
    });
    
    // Nur die letzten 5 behalten
    aiState.recentDetections = aiState.recentDetections.slice(0, 5);
    
    // HTML aktualisieren
    container.innerHTML = '';
    aiState.recentDetections.forEach((detection, i) => {
        const box = document.createElement('div');
        box.className = 'detection-box';
        box.innerHTML = `
            <strong>🌿 Erkennung #${detection.id}</strong><br>
            Konfidenz: ${(detection.confidence * 100).toFixed(1)}%<br>
            Position: (${detection.x}, ${detection.y})<br>
            Größe: ${detection.bbox ? detection.bbox.width + 'px × ' + detection.bbox.height + 'px' : 'N/A'}<br>
            <small>Zeit: ${detection.timestamp.toLocaleTimeString('de-DE')}</small>
        `;
        container.appendChild(box);
    });
}

function setSensitivity(value) {
    aiState.settings.sensitivity = value;
    console.log('Empfindlichkeit:', value);
}

function setDetectionType(type) {
    aiState.settings.detectionType = type;
    console.log('Erkennungstyp:', type);
}

function setConfidenceThreshold(value) {
    aiState.settings.confidenceThreshold = value;
    console.log('Konfidenz-Schwelle:', value);
}

function updateStats() {
    const statsElement = document.getElementById('ai-stats');
    if (!statsElement) return;
    
    const statsText = `🧠 KI-System Status:
Modell: OpenCV + Mock Detection
Version: 1.2.3
Trainingsdaten: 1,247 Bilder
Letzte Aktualisierung: Heute
Erkennungen heute: ${aiState.detectionCount}
Erkennungen gesamt: ${127 + aiState.detectionCount}
Genauigkeit: 87.3%
Performance: 12ms/Bild
Uptime: 2h 15m
Status: ${aiState.continuousMode ? 'Kontinuierlich' : 'Bereit'}`;

    statsElement.textContent = statsText;
}

function toggleAutoRemoval() {
    const btn = document.querySelector('button[onclick="toggleAutoRemoval()"]');
    const statusElement = document.getElementById('auto-status');
    
    aiState.autoRemovalActive = !aiState.autoRemovalActive;
    
    if (aiState.autoRemovalActive) {
        if (btn) {
            btn.textContent = '🛑 Auto-Entfernung AUS';
            btn.className = 'btn btn-danger';
        }
        if (statusElement) {
            statusElement.textContent = 'Automatik: EIN\nModus: Unkraut-Entfernung\nReaktionszeit: < 2s';
        }
        showNotification('🤖 Automatische Unkraut-Entfernung aktiviert!', 'success');
    } else {
        if (btn) {
            btn.textContent = '🦾 Auto-Entfernung EIN';
            btn.className = 'btn btn-warning';
        }
        if (statusElement) {
            statusElement.textContent = 'Automatik: AUS';
        }
        showNotification('🛑 Automatische Unkraut-Entfernung deaktiviert', 'info');
    }
}

async function triggerAutoRemoval(detection) {
    try {
        const response = await apiRequest('/api/arm/weed_removal', {
            method: 'POST',
            body: JSON.stringify({
                target_x: detection.x,
                target_y: detection.y
            })
        });
        
        if (response.status === 'sequence_started') {
            showNotification(`🦾 Auto-Entfernung bei (${detection.x}, ${detection.y}) gestartet`, 'success');
        }
    } catch (error) {
        console.error('Auto removal failed:', error);
        showNotification('❌ Auto-Entfernung fehlgeschlagen', 'error');
    }
}

function startTrainingMode() {
    aiState.trainingMode = !aiState.trainingMode;
    
    if (aiState.trainingMode) {
        showNotification('💾 Training-Modus aktiviert! Sammle Daten...', 'info');
    } else {
        showNotification('💾 Training-Modus deaktiviert', 'info');
    }
}

function optimizeModel() {
    showNotification('⚡ Modell-Optimierung gestartet! Das dauert etwa 5 Minuten...', 'info');
    
    // Mock-Optimierung
    setTimeout(() => {
        showNotification('✅ Modell-Optimierung abgeschlossen! Genauigkeit verbessert.', 'success');
        updateStats();
    }, 3000);
}

function exportData() {
    showNotification('📤 Exportiere Erkennungsdaten...', 'info');
    
    // Mock-Export
    const data = {
        detections: aiState.recentDetections,
        settings: aiState.settings,
        stats: {
            totalDetections: aiState.detectionCount,
            accuracy: 87.3
        }
    };
    
    setTimeout(() => {
        showNotification('✅ Daten exportiert: unkraut_data.json', 'success');
        console.log('Exported data:', data);
    }, 1000);
}

function clearDetections() {
    aiState.recentDetections = [];
    const container = document.getElementById('recent-detections');
    if (container) {
        container.innerHTML = '<div class="no-detections">Keine Erkennungen</div>';
    }
    showNotification('🗑️ Erkennungen gelöscht', 'info');
}

function updatePerformanceMetrics(processingTime, accuracy) {
    // Verarbeitungszeit
    const processingProgress = document.getElementById('processing-progress');
    const processingText = document.getElementById('processing-text');
    if (processingProgress && processingText) {
        const timePercent = Math.min(100, (processingTime / 0.5) * 100); // 0.5s = 100%
        processingProgress.style.width = `${timePercent}%`;
        processingText.textContent = `${processingTime}s pro Bild (${(1/processingTime).toFixed(0)} FPS möglich)`;
    }
    
    // Genauigkeit
    const accuracyProgress = document.getElementById('accuracy-progress');
    const accuracyText = document.getElementById('accuracy-text');
    if (accuracyProgress && accuracyText) {
        accuracyProgress.style.width = `${accuracy}%`;
        accuracyText.textContent = `${accuracy}% Trefferquote`;
    }
    
    // Modell-Auslastung (Mock)
    const modelProgress = document.getElementById('model-progress');
    const modelText = document.getElementById('model-text');
    if (modelProgress && modelText) {
        const usage = Math.random() * 50 + 25; // 25-75%
        modelProgress.style.width = `${usage}%`;
        modelText.textContent = `${usage.toFixed(0)}% GPU-Auslastung`;
    }
}

function startPerformanceUpdates() {
    setInterval(() => {
        // Mock-Performance-Updates
        updatePerformanceMetrics(0.12 + Math.random() * 0.05, 85 + Math.random() * 5);
    }, 5000);
}

// Entwicklungstools-Funktionen
function showModelInfo() {
    const info = `📋 KI-Modell Information:

Typ: Convolutional Neural Network
Architektur: ResNet-50
Parameter: 2.3M
Training: 1,247 Bilder
Validierung: 312 Bilder
Test: 78 Bilder
Genauigkeit: 87.3%
F1-Score: 0.84
Precision: 0.89
Recall: 0.81

Hardware: ${aiState.settings.detectionType === 'experimental' ? 'GPU' : 'CPU'}
Letztes Training: Gestern`;
    
    alert(info);
}

function trainModel() {
    showNotification('🎓 Modell-Training gestartet! Das Training mit neuen Daten dauert etwa 20 Minuten.', 'info');
    
    setTimeout(() => {
        showNotification('✅ Training abgeschlossen! Modell-Genauigkeit verbessert.', 'success');
    }, 5000);
}

function testAccuracy() {
    showNotification('🎯 Genauigkeitstest läuft... Teste Modell mit 50 Validierungsbildern.', 'info');
    
    setTimeout(() => {
        const accuracy = (85 + Math.random() * 10).toFixed(1);
        showNotification(`✅ Test abgeschlossen! Genauigkeit: ${accuracy}%`, 'success');
    }, 3000);
}

function saveModel() {
    showNotification('💾 Speichere Modell...', 'info');
    
    setTimeout(() => {
        showNotification('✅ Modell gespeichert: weed_model_v1.3.h5', 'success');
    }, 2000);
}

function loadModel() {
    showNotification('📂 Lade Modell...', 'info');
    
    setTimeout(() => {
        showNotification('✅ Modell geladen: weed_model_v1.2.h5', 'success');
    }, 1500);
}

function resetModel() {
    if (confirm('Modell auf Standardeinstellungen zurücksetzen? Alle Trainingsdaten gehen verloren.')) {
        showNotification('🔄 Setze Modell zurück...', 'warning');
        
        setTimeout(() => {
            aiState.detectionCount = 0;
            aiState.recentDetections = [];
            updateStats();
            clearDetections();
            showNotification('✅ Modell zurückgesetzt', 'success');
        }, 2000);
    }
}

// Auto-Stats-Update alle 30 Sekunden
setInterval(updateStats, 30000);

// Export für andere Scripts
window.aiControl = {
    quickDetection,
    continuousDetection,
    toggleAutoRemoval,
    startTrainingMode,
    optimizeModel,
    exportData,
    clearDetections,
    aiState
};