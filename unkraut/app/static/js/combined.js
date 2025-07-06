// app/static/js/combined.js - Kombinierte Kamera + Roboterarm Steuerung

let combinedState = {
    camera: {
        isStreaming: true,
        continuousDetection: false,
        detectionInterval: null
    },
    arm: {
        isMoving: false,
        emergencyStopped: false,
        currentPositions: {}
    }
};

// Initialisierung
document.addEventListener('DOMContentLoaded', function() {
    setupCombinedControls();
    startStatusUpdates();
    
    // Mock-Kamera starten falls echter Stream nicht verfügbar
    setTimeout(() => {
        const cameraStream = document.getElementById('camera-stream');
        if (cameraStream && !cameraStream.complete) {
            cameraStream.src = createMockCameraImage();
            showNotification('🎬 Mock-Kamera gestartet - simulierte Gartenansicht', 'info');
        }
    }, 2000);
    
    // Mock-Kamera alle 5 Sekunden aktualisieren für "Live"-Effekt
    setInterval(refreshMockCamera, 5000);
    
    console.log('📹🦾 Kombinierte Steuerung geladen');
});

function setupCombinedControls() {
    setupServoControls();
    setupCameraControls();
}

function setupServoControls() {
    const servos = ['tool', 'gripper', 'wrist', 'elbow', 'shoulder', 'base'];
    
    servos.forEach(servo => {
        const slider = document.getElementById(`servo-${servo}`);
        const angleDisplay = document.getElementById(`${servo}-angle`);
        
        if (slider && angleDisplay) {
            slider.addEventListener('input', function() {
                const angle = parseInt(this.value);
                angleDisplay.textContent = angle;
                
                clearTimeout(slider.timeout);
                slider.timeout = setTimeout(() => {
                    moveServo(servo, angle);
                }, 50);
            });
        }
    });
}

function setupCameraControls() {
    const cameraStream = document.getElementById('camera-stream');
    if (cameraStream) {
        cameraStream.addEventListener('error', function() {
            // Mock-Kamera anzeigen wenn echter Stream fehlschlägt
            this.src = createMockCameraImage();
            this.alt = 'Kamera im Mock-Modus';
            showNotification('📷 Kamera-Stream im Mock-Modus', 'warning');
        });
        
        cameraStream.addEventListener('load', function() {
            // Prüfen ob es sich um ein Mock-Bild handelt
            if (this.src.includes('data:image')) {
                showNotification('🔄 Mock-Kamera aktiv - simulierte Ansicht', 'info');
            } else {
                console.log('📹 Echte Kamera-Stream geladen');
            }
        });
    }
}

function createMockCameraImage() {
    // Erstelle ein SVG-Bild das eine Mock-Kamera simuliert
    const mockSvg = `
        <svg width="640" height="480" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <pattern id="grass" x="0" y="0" width="20" height="20" patternUnits="userSpaceOnUse">
                    <rect width="20" height="20" fill="#2d5a2d"/>
                    <circle cx="10" cy="10" r="2" fill="#4a8f4a"/>
                </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#grass)"/>
            
            <!-- Mock Unkraut -->
            <circle cx="150" cy="200" r="15" fill="#228B22"/>
            <circle cx="350" cy="180" r="12" fill="#32CD32"/>
            <circle cx="480" cy="250" r="18" fill="#228B22"/>
            <circle cx="200" cy="320" r="14" fill="#32CD32"/>
            <circle cx="520" cy="350" r="16" fill="#228B22"/>
            
            <!-- Kamera Info -->
            <rect x="10" y="10" width="300" height="80" fill="rgba(0,0,0,0.7)" rx="5"/>
            <text x="20" y="30" font-family="Arial" font-size="14" fill="white">🤖 Unkraut-2025 - Pi Kamera</text>
            <text x="20" y="50" font-family="Arial" font-size="12" fill="white">Modus: MOCK</text>
            <text x="20" y="65" font-family="Arial" font-size="12" fill="white">Zeit: ${new Date().toLocaleTimeString()}</text>
            <text x="20" y="80" font-family="Arial" font-size="12" fill="white">Frame: ${Math.floor(Math.random() * 9999)}</text>
            
            <!-- Crosshair für Zielen -->
            <line x1="320" y1="230" x2="320" y2="250" stroke="red" stroke-width="2"/>
            <line x1="310" y1="240" x2="330" y2="240" stroke="red" stroke-width="2"/>
            <circle cx="320" cy="240" r="20" fill="none" stroke="red" stroke-width="1"/>
        </svg>
    `;
    
    return 'data:image/svg+xml;base64,' + btoa(mockSvg);
}

function refreshMockCamera() {
    const cameraStream = document.getElementById('camera-stream');
    if (cameraStream && cameraStream.src.includes('data:image')) {
        cameraStream.src = createMockCameraImage();
    }
}

// === KAMERA FUNKTIONEN ===
async function captureImage() {
    try {
        showNotification('📸 Nehme Foto auf...', 'info');
        
        const response = await apiRequest('/api/camera/capture', {
            method: 'POST'
        });
        
        if (response.filename) {
            showNotification(`📸 Foto gespeichert: ${response.filename}`, 'success');
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
            
            const resultText = `✅ Erkennung abgeschlossen!
🌿 Objekte: ${count}
🎯 Konfidenz: ${confidence}%
⏱️ Zeit: ${response.processing_time}s

📍 Erkennungen:
${response.detections.map((d, i) => `${i+1}. ${d.class} (${(d.confidence*100).toFixed(1)}%) bei (${d.x}, ${d.y})`).join('\n')}`;
            
            const resultsElement = document.getElementById('detection-results');
            if (resultsElement) {
                resultsElement.textContent = resultText;
            }
            
            if (count > 0) {
                showNotification(`🌿 ${count} Unkraut erkannt!`, 'success');
                
                // Auto-Roboterarm zu erstem erkannten Unkraut bewegen
                if (response.detections[0]) {
                    const detection = response.detections[0];
                    setTimeout(() => {
                        if (confirm(`Roboterarm zu erkanntem Unkraut bei (${detection.x}, ${detection.y}) bewegen?`)) {
                            weedRemovalSequence(detection.x, detection.y);
                        }
                    }, 1000);
                }
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
    
    if (combinedState.camera.isStreaming) {
        cameraStream.src = '';
        combinedState.camera.isStreaming = false;
        if (toggleBtn) toggleBtn.textContent = '▶️ Stream starten';
        showNotification('⏸️ Kamera-Stream gestoppt', 'info');
    } else {
        cameraStream.src = '/api/camera/stream';
        combinedState.camera.isStreaming = true;
        if (toggleBtn) toggleBtn.textContent = '⏸️ Stream stoppen';
        showNotification('▶️ Kamera-Stream gestartet', 'info');
    }
}

function changeQuality(quality) {
    document.getElementById('quality-display').textContent = quality;
    console.log(`Bildqualität: ${quality}%`);
}

function changeFPS(fps) {
    document.getElementById('fps-display').textContent = fps;
    console.log(`FPS: ${fps}`);
}

// === ROBOTERARM FUNKTIONEN ===
async function moveServo(joint, angle) {
    if (combinedState.arm.emergencyStopped) {
        showNotification('🚨 Arm im Notaus-Modus!', 'warning');
        return;
    }
    
    try {
        const response = await apiRequest('/api/arm/move/joint', {
            method: 'POST',
            body: JSON.stringify({
                joint: joint,
                angle: angle
            })
        });
        
        if (response.status === 'success') {
            combinedState.arm.currentPositions[joint] = angle;
            console.log(`🦾 ${joint}: ${angle}°`);
        } else {
            showNotification(`❌ Servo-Fehler: ${response.error}`, 'error');
        }
        
    } catch (error) {
        console.error('Servo command failed:', error);
        showNotification('❌ Servo-Steuerung fehlgeschlagen', 'error');
    }
}

async function moveToPreset(preset) {
    if (combinedState.arm.emergencyStopped) {
        showNotification('🚨 Arm im Notaus-Modus!', 'warning');
        return;
    }
    
    try {
        combinedState.arm.isMoving = true;
        showNotification(`🎯 Fahre zu Position: ${preset}`, 'info');
        
        const response = await apiRequest('/api/arm/move/preset', {
            method: 'POST',
            body: JSON.stringify({
                preset: preset,
                duration: 2.0
            })
        });
        
        if (response.status === 'success') {
            showNotification(`✅ Position ${preset} erreicht`, 'success');
            
            setTimeout(() => {
                getArmStatus();
                combinedState.arm.isMoving = false;
            }, 2500);
        } else {
            combinedState.arm.isMoving = false;
            showNotification(`❌ Preset-Fehler: ${response.error}`, 'error');
        }
        
    } catch (error) {
        combinedState.arm.isMoving = false;
        console.error('Preset movement failed:', error);
        showNotification('❌ Preset-Bewegung fehlgeschlagen', 'error');
    }
}

async function emergencyStop() {
    try {
        const response = await apiRequest('/api/arm/emergency_stop', {
            method: 'POST'
        });
        
        combinedState.arm.emergencyStopped = true;
        combinedState.arm.isMoving = false;
        
        const sliders = document.querySelectorAll('input[type="range"]');
        sliders.forEach(slider => {
            slider.disabled = true;
        });
        
        setTimeout(() => {
            sliders.forEach(slider => {
                slider.disabled = false;
            });
            combinedState.arm.emergencyStopped = false;
            showNotification('✅ Notaus zurückgesetzt', 'success');
        }, 3000);
        
        showNotification('🚨 ROBOTERARM NOT-STOPP AKTIVIERT', 'warning');
        
    } catch (error) {
        console.error('Emergency stop failed:', error);
        showNotification('❌ Notaus fehlgeschlagen', 'error');
    }
}

async function weedRemovalSequence(targetX = 0, targetY = 0) {
    if (combinedState.arm.emergencyStopped) {
        showNotification('🚨 Arm im Notaus-Modus!', 'warning');
        return;
    }
    
    try {
        combinedState.arm.isMoving = true;
        showNotification('🌿 Unkraut-Entfernung Sequenz gestartet', 'info');
        
        const response = await apiRequest('/api/arm/weed_removal', {
            method: 'POST',
            body: JSON.stringify({
                target_x: targetX,
                target_y: targetY
            })
        });
        
        if (response.status === 'sequence_started') {
            showNotification(`🌿 Sequenz läuft bei (${targetX}, ${targetY})...`, 'success');
            
            setTimeout(() => {
                combinedState.arm.isMoving = false;
                showNotification('✅ Unkraut-Entfernung abgeschlossen', 'success');
                getArmStatus();
            }, 10000);
        } else {
            combinedState.arm.isMoving = false;
            showNotification('❌ Sequenz-Fehler', 'error');
        }
        
    } catch (error) {
        combinedState.arm.isMoving = false;
        console.error('Weed removal failed:', error);
        showNotification('❌ Unkraut-Entfernung fehlgeschlagen', 'error');
    }
}

async function activateTool() {
    if (combinedState.arm.emergencyStopped) {
        showNotification('🚨 Arm im Notaus-Modus!', 'warning');
        return;
    }
    
    try {
        showNotification('🔧 Werkzeug aktiviert für 3 Sekunden', 'info');
        
        const response = await apiRequest('/api/arm/tool/activate', {
            method: 'POST',
            body: JSON.stringify({
                duration: 3.0
            })
        });
        
        if (response.status === 'tool_activated') {
            const toolSlider = document.getElementById('servo-tool');
            if (toolSlider) {
                toolSlider.style.background = 'linear-gradient(to right, #ffc107, #fd7e14)';
                
                setTimeout(() => {
                    toolSlider.style.background = '';
                    showNotification('🔧 Werkzeug gestoppt', 'success');
                }, 3000);
            }
        } else {
            showNotification('❌ Werkzeug-Aktivierung fehlgeschlagen', 'error');
        }
        
    } catch (error) {
        console.error('Tool activation failed:', error);
        showNotification('❌ Werkzeug-Fehler', 'error');
    }
}

async function getArmStatus() {
    try {
        const data = await apiRequest('/api/arm/info');
        
        const statusText = `Hardware: ${data.controller?.hardware_available ? 'Echt (PCA9685)' : 'Mock'}
I2C: ${data.controller?.i2c_address || 'N/A'}
Servos: ${data.controller?.servo_count || 0}
Status: ${combinedState.arm.isMoving ? 'Bewegt sich' : 'Bereit'}

Position:
${Object.entries(data.current_position || {}).map(([joint, angle]) => `${joint}: ${angle}°`).join('\n')}`;

        const statusElement = document.getElementById('arm-status');
        if (statusElement) {
            statusElement.textContent = statusText;
        }
        
        // Slider-Positionen aktualisieren
        if (data.current_position) {
            Object.entries(data.current_position).forEach(([joint, angle]) => {
                const slider = document.getElementById(`servo-${joint}`);
                const angleDisplay = document.getElementById(`${joint}-angle`);
                
                if (slider && !combinedState.arm.isMoving) {
                    slider.value = angle;
                }
                if (angleDisplay) {
                    angleDisplay.textContent = angle;
                }
                
                combinedState.arm.currentPositions[joint] = angle;
            });
        }
        
    } catch (error) {
        console.error('Status update failed:', error);
        const statusElement = document.getElementById('arm-status');
        if (statusElement) {
            statusElement.textContent = '❌ Status nicht verfügbar';
        }
    }
}

function startStatusUpdates() {
    getArmStatus();
    setInterval(getArmStatus, 5000);
}

// API Helper Function
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

// Notification System
function showNotification(message, type = 'info') {
    const existing = document.querySelector('.notification');
    if (existing) {
        existing.remove();
    }
    
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
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
    
    const colors = {
        success: '#28a745',
        error: '#dc3545',
        warning: '#ffc107',
        info: '#17a2b8'
    };
    
    notification.style.backgroundColor = colors[type] || colors.info;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.opacity = '1';
        notification.style.transform = 'translateY(0)';
    }, 100);
    
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

// Export für andere Scripts
window.combinedControl = {
    captureImage,
    detectWeeds,
    toggleStream,
    moveServo,
    moveToPreset,
    emergencyStop,
    weedRemovalSequence,
    activateTool,
    getArmStatus,
    combinedState
};