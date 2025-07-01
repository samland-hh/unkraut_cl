/* app/static/js/control.js */
class RobotController {
    constructor() {
        this.isConnected = false;
        this.currentCommand = null;
        this.init();
    }

    init() {
        this.setupVehicleControls();
        this.setupArmControls();
        this.setupKeyboardControls();
        this.setupEmergencyStop();
        this.startHeartbeat();
    }

    // Fahrzeug Steuerung
    setupVehicleControls() {
        const buttons = document.querySelectorAll('.vehicle-controls .control-btn');
        
        buttons.forEach(btn => {
            btn.addEventListener('mousedown', (e) => {
                const action = e.target.dataset.action;
                this.sendVehicleCommand(action);
                btn.style.background = 'linear-gradient(145deg, #45a049, #4CAF50)';
            });
            
            btn.addEventListener('mouseup', (e) => {
                this.sendVehicleCommand('stop');
                btn.style.background = 'linear-gradient(145deg, #4CAF50, #45a049)';
            });
            
            btn.addEventListener('mouseleave', (e) => {
                this.sendVehicleCommand('stop');
                btn.style.background = 'linear-gradient(145deg, #4CAF50, #45a049)';
            });
        });
    }

    // Roboterarm Steuerung
    setupArmControls() {
        const servos = ['Base', 'Shoulder', 'Elbow', 'Wrist', 'Gripper'];
        
        servos.forEach(servo => {
            const slider = document.getElementById(`servo${servo}`);
            const valueDisplay = document.getElementById(`value${servo}`);
            
            slider.addEventListener('input', (e) => {
                const value = e.target.value;
                valueDisplay.textContent = `${value}°`;
                this.sendServoCommand(servo.toLowerCase(), value);
            });
        });
    }

    // Tastatur Steuerung
    setupKeyboardControls() {
        let pressedKeys = new Set();
        
        document.addEventListener('keydown', (e) => {
            if (pressedKeys.has(e.code)) return;
            pressedKeys.add(e.code);
            
            switch(e.code) {
                case 'ArrowUp':
                case 'KeyW':
                    this.sendVehicleCommand('forward');
                    break;
                case 'ArrowDown':
                case 'KeyS':
                    this.sendVehicleCommand('backward');
                    break;
                case 'ArrowLeft':
                case 'KeyA':
                    this.sendVehicleCommand('left');
                    break;
                case 'ArrowRight':
                case 'KeyD':
                    this.sendVehicleCommand('right');
                    break;
                case 'Space':
                    e.preventDefault();
                    this.sendVehicleCommand('stop');
                    break;
            }
        });
        
        document.addEventListener('keyup', (e) => {
            pressedKeys.delete(e.code);
            if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'KeyW', 'KeyA', 'KeyS', 'KeyD'].includes(e.code)) {
                this.sendVehicleCommand('stop');
            }
        });
    }

    // Notaus
    setupEmergencyStop() {
        document.getElementById('emergencyStop').addEventListener('click', () => {
            this.emergencyStop();
        });
    }

    // API Aufrufe
    async sendVehicleCommand(command) {
        try {
            const response = await fetch('/api/vehicle/move', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ command: command })
            });
            
            if (!response.ok) {
                console.error('Fahrzeug Kommando fehlgeschlagen:', command);
            }
        } catch (error) {
            console.error('Verbindungsfehler:', error);
            this.showConnectionError();
        }
    }

    async sendServoCommand(servo, angle) {
        try {
            const response = await fetch('/api/arm/servo', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    servo: servo, 
                    angle: parseInt(angle) 
                })
            });
            
            if (!response.ok) {
                console.error('Servo Kommando fehlgeschlagen:', servo, angle);
            }
        } catch (error) {
            console.error('Verbindungsfehler:', error);
            this.showConnectionError();
        }
    }

    async emergencyStop() {
        try {
            await fetch('/api/emergency/stop', {
                method: 'POST'
            });
            
            // Alle Slider auf Neutralposition
            document.querySelectorAll('.slider').forEach(slider => {
                slider.value = 90;
                const servo = slider.id.replace('servo', '').toLowerCase();
                document.getElementById(`value${slider.id.replace('servo', '')}`).textContent = '90°';
            });
            
            alert('🛑 NOTAUS AKTIVIERT! Alle Systeme gestoppt.');
        } catch (error) {
            console.error('Notaus fehlgeschlagen:', error);
        }
    }

    // Verbindung überwachen
    async startHeartbeat() {
        setInterval(async () => {
            try {
                const response = await fetch('/api/status');
                if (response.ok) {
                    if (!this.isConnected) {
                        this.isConnected = true;
                        this.updateConnectionStatus(true);
                    }
                } else {
                    throw new Error('Server nicht erreichbar');
                }
            } catch (error) {
                if (this.isConnected) {
                    this.isConnected = false;
                    this.updateConnectionStatus(false);
                }
            }
        }, 2000);
    }

    updateConnectionStatus(connected) {
        const dots = document.querySelectorAll('.status-dot');
        dots.forEach(dot => {
            dot.style.background = connected ? '#4CAF50' : '#f44336';
        });
    }

    showConnectionError() {
        const overlay = document.querySelector('.camera-overlay');
        overlay.innerHTML = '<div>❌ Verbindung unterbrochen</div>';
        setTimeout(() => {
            overlay.innerHTML = '<div>📡 Live Stream</div><div id="streamInfo">640x480 @ 30fps</div>';
        }, 3000);
    }
}

// Kamera Stream Fehlerbehandlung
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('cameraStream').addEventListener('error', function() {
        this.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjQwIiBoZWlnaHQ9IjQ4MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjMzMzIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxOCIgZmlsbD0iI2ZmZiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPvCfk7kgS2FtZXJhIG5pY2h0IHZlcmbDvGdiYXI8L3RleHQ+PC9zdmc+';
        this.alt = 'Kamera nicht verfügbar';
    });

    // Controller initialisieren
    const controller = new RobotController();

    // Touch Events für Mobile
    if ('ontouchstart' in window) {
        document.querySelectorAll('.control-btn').forEach(btn => {
            btn.addEventListener('touchstart', (e) => {
                e.preventDefault();
                btn.dispatchEvent(new Event('mousedown'));
            });
            
            btn.addEventListener('touchend', (e) => {
                e.preventDefault();
                btn.dispatchEvent(new Event('mouseup'));
            });
        });
    }

    console.log('🤖 Unkraut-2025 Steuerung geladen');
});