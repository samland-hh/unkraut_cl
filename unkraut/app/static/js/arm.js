// app/static/js/arm.js - Roboterarm JavaScript

let armStatus = {
    isMoving: false,
    emergencyStopped: false,
    currentPositions: {}
};

// Initialisierung
document.addEventListener('DOMContentLoaded', function() {
    setupServoControls();
    startStatusUpdates();
    
    console.log('🦾 Roboterarm-Steuerung geladen');
});

function setupServoControls() {
    const servos = ['base', 'shoulder', 'elbow', 'wrist', 'gripper', 'tool'];
    
    servos.forEach(servo => {
        const slider = document.getElementById(`servo-${servo}`);
        const angleDisplay = document.getElementById(`${servo}-angle`);
        const valueDisplay = document.getElementById(`value-${servo}`);
        
        if (slider && angleDisplay && valueDisplay) {
            slider.addEventListener('input', function() {
                const angle = parseInt(this.value);
                angleDisplay.textContent = angle;
                valueDisplay.textContent = `${angle}°`;
                
                // Throttle servo commands to avoid spam
                clearTimeout(slider.timeout);
                slider.timeout = setTimeout(() => {
                    moveServo(servo, angle);
                }, 50);
            });
        }
    });
}

async function moveServo(joint, angle) {
    if (armStatus.emergencyStopped) {
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
            armStatus.currentPositions[joint] = angle;
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
    if (armStatus.emergencyStopped) {
        showNotification('🚨 Arm im Notaus-Modus!', 'warning');
        return;
    }
    
    try {
        armStatus.isMoving = true;
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
            
            // Status nach Bewegung aktualisieren
            setTimeout(() => {
                getArmStatus();
                armStatus.isMoving = false;
            }, 2500);
        } else {
            armStatus.isMoving = false;
            showNotification(`❌ Preset-Fehler: ${response.error}`, 'error');
        }
        
    } catch (error) {
        armStatus.isMoving = false;
        console.error('Preset movement failed:', error);
        showNotification('❌ Preset-Bewegung fehlgeschlagen', 'error');
    }
}

async function emergencyStop() {
    try {
        const response = await apiRequest('/api/arm/emergency_stop', {
            method: 'POST'
        });
        
        armStatus.emergencyStopped = true;
        armStatus.isMoving = false;
        
        // Alle Slider deaktivieren für 3 Sekunden
        const sliders = document.querySelectorAll('input[type="range"]');
        sliders.forEach(slider => {
            slider.disabled = true;
        });
        
        setTimeout(() => {
            sliders.forEach(slider => {
                slider.disabled = false;
            });
            armStatus.emergencyStopped = false;
            showNotification('✅ Notaus zurückgesetzt', 'success');
        }, 3000);
        
        showNotification('🚨 ROBOTERARM NOT-STOPP AKTIVIERT', 'warning');
        
    } catch (error) {
        console.error('Emergency stop failed:', error);
        showNotification('❌ Notaus fehlgeschlagen', 'error');
    }
}

async function weedRemovalSequence() {
    if (armStatus.emergencyStopped) {
        showNotification('🚨 Arm im Notaus-Modus!', 'warning');
        return;
    }
    
    if (!confirm('Unkraut-Entfernung Sequenz starten?')) {
        return;
    }
    
    try {
        armStatus.isMoving = true;
        showNotification('🌿 Unkraut-Entfernung Sequenz gestartet', 'info');
        
        const response = await apiRequest('/api/arm/weed_removal', {
            method: 'POST',
            body: JSON.stringify({
                target_x: 0,
                target_y: 0
            })
        });
        
        if (response.status === 'sequence_started') {
            showNotification('🌿 Sequenz läuft...', 'success');
            
            // Status verfolgen
            setTimeout(() => {
                armStatus.isMoving = false;
                showNotification('✅ Unkraut-Entfernung abgeschlossen', 'success');
                getArmStatus();
            }, 10000); // 10 Sekunden für komplette Sequenz
        } else {
            armStatus.isMoving = false;
            showNotification('❌ Sequenz-Fehler', 'error');
        }
        
    } catch (error) {
        armStatus.isMoving = false;
        console.error('Weed removal failed:', error);
        showNotification('❌ Unkraut-Entfernung fehlgeschlagen', 'error');
    }
}

async function activateTool() {
    if (armStatus.emergencyStopped) {
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
            // Tool-Status visuell anzeigen
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

async function calibrateServos() {
    if (armStatus.emergencyStopped) {
        showNotification('🚨 Arm im Notaus-Modus!', 'warning');
        return;
    }
    
    if (!confirm('Servo-Kalibrierung starten? Das dauert etwa 30 Sekunden.')) {
        return;
    }
    
    try {
        armStatus.isMoving = true;
        showNotification('⚙️ Servo-Kalibrierung gestartet', 'info');
        
        const response = await apiRequest('/api/arm/calibrate', {
            method: 'POST'
        });
        
        if (response.status === 'calibration_started') {
            // Alle Slider während Kalibrierung deaktivieren
            const sliders = document.querySelectorAll('input[type="range"]');
            sliders.forEach(slider => {
                slider.disabled = true;
            });
            
            // Nach 30 Sekunden wieder aktivieren
            setTimeout(() => {
                sliders.forEach(slider => {
                    slider.disabled = false;
                });
                armStatus.isMoving = false;
                showNotification('✅ Servo-Kalibrierung abgeschlossen', 'success');
                getArmStatus();
            }, 30000);
            
        } else {
            armStatus.isMoving = false;
            showNotification('❌ Kalibrierung-Fehler', 'error');
        }
        
    } catch (error) {
        armStatus.isMoving = false;
        console.error('Calibration failed:', error);
        showNotification('❌ Kalibrierung fehlgeschlagen', 'error');
    }
}

async function getArmStatus() {
    try {
        const data = await apiRequest('/api/arm/info');
        
        const statusText = `Hardware: ${data.controller?.hardware_available ? 'Echt (PCA9685)' : 'Mock'}
I2C Adresse: ${data.controller?.i2c_address || 'N/A'}
Servos: ${data.controller?.servo_count || 0}
Gelenke: ${data.joints?.join(', ') || 'N/A'}
Presets: ${data.presets?.join(', ') || 'N/A'}
Status: ${armStatus.isMoving ? 'Bewegt sich' : 'Bereit'}

Aktuelle Position:
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
                const valueDisplay = document.getElementById(`value-${joint}`);
                
                if (slider && !armStatus.isMoving) {
                    slider.value = angle;
                }
                if (angleDisplay) {
                    angleDisplay.textContent = angle;
                }
                if (valueDisplay) {
                    valueDisplay.textContent = `${angle}°`;
                }
                
                armStatus.currentPositions[joint] = angle;
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
    // Sofort laden
    getArmStatus();
    
    // Alle 5 Sekunden aktualisieren
    setInterval(getArmStatus, 5000);
}

// Export für andere Scripts
window.armControl = {
    moveServo,
    moveToPreset,
    emergencyStop,
    weedRemovalSequence,
    activateTool,
    calibrateServos,
    getArmStatus,
    armStatus
};