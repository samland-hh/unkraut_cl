// app/static/js/control.js - Fahrzeug-Steuerung JavaScript

let currentSpeed = 50;
let isMoving = false;
let moveInterval = null;

// Initialisierung
document.addEventListener('DOMContentLoaded', function() {
    setupVehicleControls();
    setupKeyboardControls();
    setupSpeedControl();
    startStatusUpdates();
    
    console.log('🎮 Fahrzeug-Steuerung geladen');
});

function setupVehicleControls() {
    const controlButtons = document.querySelectorAll('.control-btn');
    
    controlButtons.forEach(btn => {
        const direction = btn.dataset.direction;
        if (!direction) return;
        
        // Mouse Events
        btn.addEventListener('mousedown', () => startMove(direction, btn));
        btn.addEventListener('mouseup', () => stopMove(btn));
        btn.addEventListener('mouseleave', () => stopMove(btn));
        
        // Touch Events für Mobile
        btn.addEventListener('touchstart', (e) => {
            e.preventDefault();
            startMove(direction, btn);
        });
        
        btn.addEventListener('touchend', (e) => {
            e.preventDefault();
            stopMove(btn);
        });
    });
}

function setupKeyboardControls() {
    let pressedKeys = new Set();
    
    document.addEventListener('keydown', (e) => {
        // Nur wenn kein Input fokussiert ist
        if (document.activeElement.tagName === 'INPUT') return;
        
        if (pressedKeys.has(e.code)) return;
        pressedKeys.add(e.code);
        
        let direction = null;
        switch(e.code) {
            case 'ArrowUp':
            case 'KeyW':
                direction = 'forward';
                break;
            case 'ArrowDown':
            case 'KeyS':
                direction = 'backward';
                break;
            case 'ArrowLeft':
            case 'KeyA':
                direction = 'left';
                break;
            case 'ArrowRight':
            case 'KeyD':
                direction = 'right';
                break;
            case 'Space':
                e.preventDefault();
                emergencyStop();
                return;
        }
        
        if (direction) {
            e.preventDefault();
            const btn = document.querySelector(`[data-direction="${direction}"]`);
            startMove(direction, btn);
        }
    });
    
    document.addEventListener('keyup', (e) => {
        pressedKeys.delete(e.code);
        
        const keyDirections = {
            'ArrowUp': 'forward',
            'KeyW': 'forward',
            'ArrowDown': 'backward', 
            'KeyS': 'backward',
            'ArrowLeft': 'left',
            'KeyA': 'left',
            'ArrowRight': 'right',
            'KeyD': 'right'
        };
        
        const direction = keyDirections[e.code];
        if (direction) {
            const btn = document.querySelector(`[data-direction="${direction}"]`);
            stopMove(btn);
        }
    });
}

function setupSpeedControl() {
    const speedSlider = document.getElementById('speed-slider');
    const speedDisplay = document.getElementById('speed-display');
    
    if (speedSlider && speedDisplay) {
        speedSlider.addEventListener('input', function() {
            currentSpeed = parseInt(this.value);
            speedDisplay.textContent = currentSpeed;
            
            // Speed visuell anzeigen
            if (currentSpeed < 30) {
                speedDisplay.style.color = '#28a745'; // Grün
            } else if (currentSpeed < 70) {
                speedDisplay.style.color = '#ffc107'; // Gelb
            } else {
                speedDisplay.style.color = '#dc3545'; // Rot
            }
        });
    }
}

function startMove(direction, btn) {
    if (isMoving) return;
    
    isMoving = true;
    
    // Button visuell aktivieren
    if (btn) {
        btn.style.background = 'linear-gradient(145deg, #218838, #1e7e34)';
        btn.style.transform = 'translateY(2px)';
    }
    
    // Erste Bewegung sofort
    sendMoveCommand(direction);
    
    // Kontinuierliche Bewegung alle 100ms
    moveInterval = setInterval(() => {
        sendMoveCommand(direction);
    }, 100);
    
    showNotification(`🚗 Fahre ${getDirectionText(direction)}`, 'info');
}

function stopMove(btn) {
    if (!isMoving) return;
    
    isMoving = false;
    
    // Interval stoppen
    if (moveInterval) {
        clearInterval(moveInterval);
        moveInterval = null;
    }
    
    // Button visuell zurücksetzen
    if (btn) {
        btn.style.background = '';
        btn.style.transform = '';
    }
    
    // Stopp-Befehl senden
    sendStopCommand();
}

async function sendMoveCommand(direction) {
    try {
        const response = await apiRequest('/api/control/move', {
            method: 'POST',
            body: JSON.stringify({
                direction: direction,
                speed: currentSpeed,
                duration: 0.1
            })
        });
        
        // Erfolg - kein Notification um Spam zu vermeiden
        
    } catch (error) {
        console.error('Move command failed:', error);
        isMoving = false;
        if (moveInterval) {
            clearInterval(moveInterval);
            moveInterval = null;
        }
        showNotification('❌ Bewegung fehlgeschlagen', 'error');
    }
}

async function sendStopCommand() {
    try {
        await apiRequest('/api/control/stop', {
            method: 'POST'
        });
    } catch (error) {
        console.error('Stop command failed:', error);
        showNotification('❌ Stopp fehlgeschlagen', 'error');
    }
}

function emergencyStop() {
    // Alle Bewegungen sofort stoppen
    isMoving = false;
    if (moveInterval) {
        clearInterval(moveInterval);
        moveInterval = null;
    }
    
    // Alle Buttons zurücksetzen
    document.querySelectorAll('.control-btn').forEach(btn => {
        btn.style.background = '';
        btn.style.transform = '';
    });
    
    // Not-Stopp API aufrufen
    sendStopCommand();
    
    showNotification('🚨 NOT-STOPP AKTIVIERT', 'warning');
}

function getDirectionText(direction) {
    const texts = {
        'forward': 'vorwärts',
        'backward': 'rückwärts',
        'left': 'links',
        'right': 'rechts'
    };
    return texts[direction] || direction;
}

async function updateRobotStatus() {
    try {
        const data = await apiRequest('/api/control/status');
        
        const statusHtml = `
            <div><strong>Status:</strong> ${data.robot?.mode || 'Unbekannt'}</div>
            <div><strong>Motoren:</strong> ${data.robot?.motors?.is_moving ? 'Bewegt sich' : 'Gestoppt'}</div>
            <div><strong>Geschwindigkeit:</strong> ${currentSpeed}%</div>
            <div><strong>Temperatur:</strong> ${data.sensors?.temperature || 'N/A'}°C</div>
            <div><strong>Batterie:</strong> ${data.battery?.percentage || 'N/A'}%</div>
            <div><strong>Arm verfügbar:</strong> ${data.arm?.available ? 'Ja' : 'Nein'}</div>
        `;
        
        const statusElement = document.getElementById('robot-status');
        if (statusElement) {
            statusElement.innerHTML = statusHtml;
        }
        
    } catch (error) {
        console.error('Status update failed:', error);
        const statusElement = document.getElementById('robot-status');
        if (statusElement) {
            statusElement.innerHTML = '<div class="error">❌ Status nicht verfügbar</div>';
        }
    }
}

function startStatusUpdates() {
    // Sofort updaten
    updateRobotStatus();
    
    // Alle 3 Sekunden updaten
    setInterval(updateRobotStatus, 3000);
}

// Cleanup beim Verlassen der Seite
window.addEventListener('beforeunload', function() {
    if (isMoving) {
        sendStopCommand();
    }
});

// Export für andere Scripts
window.vehicleControl = {
    startMove,
    stopMove,
    emergencyStop,
    currentSpeed,
    isMoving
};