# app/routes/arm.py
"""
Flask API für Roboterarm-Steuerung
"""
from flask import Blueprint, jsonify, request, render_template
import time

bp = Blueprint('arm', __name__, url_prefix='/api/arm')

@bp.route('/info')
def get_arm_info():
    """Roboterarm-Informationen"""
    try:
        from hardware.robot_arm import robot_arm
        info = robot_arm.get_arm_info()
        return jsonify(info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/position')
def get_position():
    """Aktuelle Arm-Position"""
    try:
        from hardware.robot_arm import robot_arm
        position = robot_arm.get_current_position()
        return jsonify({'position': position})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/move/joint', methods=['POST'])
def move_joint():
    """Einzelnes Gelenk bewegen"""
    try:
        data = request.get_json()
        joint = data.get('joint')
        angle = data.get('angle')
        
        if not joint or angle is None:
            return jsonify({'error': 'Joint und Angle erforderlich'}), 400
        
        from hardware.robot_arm import robot_arm
        success = robot_arm.move_joint(joint, float(angle))
        
        if success:
            return jsonify({'status': 'success', 'joint': joint, 'angle': angle})
        else:
            return jsonify({'error': 'Bewegung fehlgeschlagen'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/move/preset', methods=['POST'])
def move_to_preset():
    """Zu Preset-Position fahren"""
    try:
        data = request.get_json()
        preset = data.get('preset')
        duration = data.get('duration', 2.0)
        
        if not preset:
            return jsonify({'error': 'Preset erforderlich'}), 400
        
        from hardware.robot_arm import robot_arm
        success = robot_arm.move_to_preset(preset, duration)
        
        if success:
            return jsonify({'status': 'success', 'preset': preset, 'duration': duration})
        else:
            return jsonify({'error': f'Preset {preset} nicht gefunden'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/move/custom', methods=['POST'])
def move_custom():
    """Zu benutzerdefinierten Positionen fahren"""
    try:
        data = request.get_json()
        positions = data.get('positions', {})
        duration = data.get('duration', 1.5)
        
        if not positions:
            return jsonify({'error': 'Positionen erforderlich'}), 400
        
        from hardware.robot_arm import robot_arm
        success = robot_arm.set_custom_position(positions, duration)
        
        if success:
            return jsonify({'status': 'success', 'positions': positions})
        else:
            return jsonify({'error': 'Bewegung fehlgeschlagen'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/weed_removal', methods=['POST'])
def weed_removal_sequence():
    """Unkraut-Entfernung Sequenz starten"""
    try:
        data = request.get_json() or {}
        target_x = data.get('target_x', 0)
        target_y = data.get('target_y', 0)
        
        from hardware.robot_arm import robot_arm
        
        # Sequenz in separatem Thread ausführen (non-blocking)
        import threading
        thread = threading.Thread(
            target=robot_arm.weed_removal_sequence,
            args=(target_x, target_y),
            daemon=True
        )
        thread.start()
        
        return jsonify({
            'status': 'sequence_started',
            'target_x': target_x,
            'target_y': target_y
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/tool/activate', methods=['POST'])
def activate_tool():
    """Werkzeug aktivieren"""
    try:
        data = request.get_json() or {}
        duration = data.get('duration', 1.0)
        
        from hardware.robot_arm import robot_arm
        
        # Tool-Aktivierung in Thread
        import threading
        thread = threading.Thread(
            target=robot_arm.activate_tool,
            args=(duration,),
            daemon=True
        )
        thread.start()
        
        return jsonify({'status': 'tool_activated', 'duration': duration})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/emergency_stop', methods=['POST'])
def emergency_stop():
    """Not-Stopp für Roboterarm"""
    try:
        from hardware.robot_arm import robot_arm
        robot_arm.emergency_stop()
        return jsonify({'status': 'emergency_stop_activated'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/home', methods=['POST'])
def home_position():
    """Zur Home-Position fahren"""
    try:
        from hardware.robot_arm import robot_arm
        success = robot_arm.home_position()
        return jsonify({'status': 'success' if success else 'failed'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/park', methods=['POST'])
def park_position():
    """Zur Park-Position fahren und Servos deaktivieren"""
    try:
        from hardware.robot_arm import robot_arm
        success = robot_arm.park_position()
        return jsonify({'status': 'success' if success else 'failed'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/calibrate', methods=['POST'])
def calibrate_servos():
    """Servo-Kalibrierung durchführen"""
    try:
        from hardware.robot_arm import robot_arm
        
        # Kalibrierung in Thread (dauert länger)
        import threading
        thread = threading.Thread(
            target=robot_arm.calibrate_servos,
            daemon=True
        )
        thread.start()
        
        return jsonify({'status': 'calibration_started'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Roboterarm-Template Route (in app/main.py hinzufügen)
def add_arm_route_to_main_app(app):
    """Füge Roboterarm-Route zur Haupt-App hinzu"""
    
    @app.route('/arm')
    def arm_control():
        return render_template('arm_control.html')

# app/templates/arm_control.html
ARM_CONTROL_TEMPLATE = '''
{% extends "base.html" %}

{% block title %}Roboterarm Steuerung - Unkraut-2025{% endblock %}

{% block content %}
<div class="container-fluid">
    <div class="row mb-4">
        <div class="col-12">
            <h2><i class="fas fa-robot"></i> Roboterarm Steuerung</h2>
        </div>
    </div>
    
    <!-- Status & Info -->
    <div class="row mb-4">
        <div class="col-lg-4">
            <div class="card">
                <div class="card-header bg-info text-white">
                    <h5><i class="fas fa-info-circle"></i> Arm Status</h5>
                </div>
                <div class="card-body">
                    <div id="arm-status">
                        <div class="text-center">
                            <div class="spinner-border text-primary" role="status">
                                <span class="visually-hidden">Lade...</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="col-lg-8">
            <div class="card">
                <div class="card-header bg-success text-white">
                    <h5><i class="fas fa-gamepad"></i> Schnellaktionen</h5>
                </div>
                <div class="card-body">
                    <div class="row text-center">
                        <div class="col-md-2 col-6 mb-3">
                            <button class="btn btn-primary w-100" onclick="moveToPreset('home')">
                                <i class="fas fa-home"></i><br>
                                <small>Home</small>
                            </button>
                        </div>
                        <div class="col-md-2 col-6 mb-3">
                            <button class="btn btn-warning w-100" onclick="moveToPreset('weed_detect')">
                                <i class="fas fa-search"></i><br>
                                <small>Erkennen</small>
                            </button>
                        </div>
                        <div class="col-md-2 col-6 mb-3">
                            <button class="btn btn-success w-100" onclick="moveToPreset('weed_remove')">
                                <i class="fas fa-cut"></i><br>
                                <small>Entfernen</small>
                            </button>
                        </div>
                        <div class="col-md-2 col-6 mb-3">
                            <button class="btn btn-info w-100" onclick="moveToPreset('spray_position')">
                                <i class="fas fa-spray-can"></i><br>
                                <small>Sprühen</small>
                            </button>
                        </div>
                        <div class="col-md-2 col-6 mb-3">
                            <button class="btn btn-secondary w-100" onclick="moveToPreset('park')">
                                <i class="fas fa-parking"></i><br>
                                <small>Parken</small>
                            </button>
                        </div>
                        <div class="col-md-2 col-6 mb-3">
                            <button class="btn btn-danger w-100" onclick="emergencyStop()">
                                <i class="fas fa-stop"></i><br>
                                <small>Not-Stopp</small>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Servo-Steuerung -->
    <div class="row mb-4">
        <div class="col-12">
            <div class="card">
                <div class="card-header bg-primary text-white">
                    <h5><i class="fas fa-sliders-h"></i> Manuelle Servo-Steuerung</h5>
                    <div class="float-end">
                        <button class="btn btn-sm btn-light" onclick="resetAllServos()">
                            <i class="fas fa-undo"></i> Reset
                        </button>
                    </div>
                </div>
                <div class="card-body">
                    <div class="row" id="servo-controls">
                        <!-- Wird per JavaScript gefüllt -->
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Automatische Sequenzen -->
    <div class="row mb-4">
        <div class="col-lg-6">
            <div class="card">
                <div class="card-header bg-success text-white">
                    <h5><i class="fas fa-magic"></i> Automatische Sequenzen</h5>
                </div>
                <div class="card-body">
                    <div class="mb-3">
                        <button class="btn btn-success w-100 mb-2" onclick="startWeedRemovalSequence()">
                            <i class="fas fa-leaf"></i> Unkraut-Entfernung Sequenz
                        </button>
                        <button class="btn btn-info w-100 mb-2" onclick="activateTool()">
                            <i class="fas fa-tools"></i> Werkzeug aktivieren (3s)
                        </button>
                        <button class="btn btn-warning w-100 mb-2" onclick="calibrateServos()">
                            <i class="fas fa-cog"></i> Servo-Kalibrierung
                        </button>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="col-lg-6">
            <div class="card">
                <div class="card-header bg-info text-white">
                    <h5><i class="fas fa-chart-line"></i> Arm-Visualisierung</h5>
                </div>
                <div class="card-body">
                    <div id="arm-visualization" class="text-center" style="min-height: 200px;">
                        <!-- Einfache ASCII-Art Darstellung des Arms -->
                        <div class="mt-4">
                            <h6>Roboterarm Schema</h6>
                            <div class="font-monospace" id="arm-ascii">
                                <div>     🤖 Base</div>
                                <div>     |</div>
                                <div>    ┌─┐ Shoulder</div>
                                <div>    └─┘</div>
                                <div>     | Elbow</div>
                                <div>     |</div>
                                <div>    ✋ Gripper</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Aktivitätslog -->
    <div class="row">
        <div class="col-12">
            <div class="card">
                <div class="card-header bg-dark text-white">
                    <h5><i class="fas fa-terminal"></i> Aktivitätslog</h5>
                    <button class="btn btn-sm btn-outline-light float-end" onclick="clearLog()">
                        <i class="fas fa-trash"></i> Löschen
                    </button>
                </div>
                <div class="card-body">
                    <div id="activity-log" class="font-monospace small" style="height: 200px; overflow-y: auto; background: #f8f9fa; padding: 10px; border-radius: 4px;">
                        <div class="text-muted">Roboterarm-Aktivitäten werden hier angezeigt...</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
// Roboterarm JavaScript
let armInfo = null;
let currentPositions = {};

// Initialisierung
document.addEventListener('DOMContentLoaded', function() {
    loadArmInfo();
    updateArmStatus();
    setInterval(updateArmStatus, 3000);
});

// Arm-Informationen laden
function loadArmInfo() {
    fetch('/api/arm/info')
        .then(response => response.json())
        .then(data => {
            armInfo = data;
            createServoControls();
            updateArmStatusDisplay();
        })
        .catch(error => {
            console.error('Fehler beim Laden der Arm-Info:', error);
            logActivity('❌ Fehler beim Laden der Arm-Informationen');
        });
}

// Servo-Steuerungen erstellen
function createServoControls() {
    if (!armInfo || !armInfo.joints) return;
    
    const container = document.getElementById('servo-controls');
    container.innerHTML = '';
    
    armInfo.joints.forEach(joint => {
        const limits = armInfo.joint_limits[joint] || [0, 180];
        const currentAngle = currentPositions[joint] || 90;
        
        const servoHtml = `
            <div class="col-lg-4 col-md-6 mb-4">
                <div class="card">
                    <div class="card-header">
                        <h6><i class="fas fa-cog"></i> ${joint.toUpperCase()}</h6>
                    </div>
                    <div class="card-body">
                        <div class="mb-2">
                            <label for="servo-${joint}" class="form-label">
                                Winkel: <span id="angle-${joint}">${currentAngle}°</span>
                            </label>
                            <input type="range" 
                                   class="form-range" 
                                   id="servo-${joint}"
                                   min="${limits[0]}" 
                                   max="${limits[1]}" 
                                   value="${currentAngle}"
                                   oninput="updateServoAngle('${joint}', this.value)">
                        </div>
                        <div class="small text-muted">
                            Bereich: ${limits[0]}° - ${limits[1]}°
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        container.insertAdjacentHTML('beforeend', servoHtml);
    });
}

// Servo-Winkel aktualisieren
function updateServoAngle(joint, angle) {
    document.getElementById(`angle-${joint}`).textContent = angle + '°';
    
    // Servo bewegen
    fetch('/api/arm/move/joint', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({joint: joint, angle: parseFloat(angle)})
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            currentPositions[joint] = parseFloat(angle);
            logActivity(`🦾 ${joint}: ${angle}°`);
        } else {
            logActivity(`❌ Fehler bei ${joint}: ${data.error}`);
        }
    })
    .catch(error => {
        console.error('Servo-Bewegung Fehler:', error);
        logActivity(`❌ Servo-Bewegung fehlgeschlagen: ${error}`);
    });
}

// Zu Preset-Position fahren
function moveToPreset(preset) {
    logActivity(`🎯 Fahre zu Position: ${preset}`);
    
    fetch('/api/arm/move/preset', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({preset: preset, duration: 2.0})
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            logActivity(`✅ Position "${preset}" erreicht`);
            // Nach 2.5s Position aktualisieren
            setTimeout(updateArmStatus, 2500);
        } else {
            logActivity(`❌ Preset-Bewegung fehlgeschlagen: ${data.error}`);
        }
    })
    .catch(error => {
        console.error('Preset-Bewegung Fehler:', error);
        logActivity(`❌ Preset-Bewegung fehlgeschlagen: ${error}`);
    });
}

// Arm-Status aktualisieren
function updateArmStatus() {
    fetch('/api/arm/position')
        .then(response => response.json())
        .then(data => {
            if (data.position) {
                currentPositions = data.position;
                updateServoSliders();
            }
        })
        .catch(error => {
            console.error('Status-Update Fehler:', error);
        });
}

// Servo-Slider aktualisieren
function updateServoSliders() {
    Object.keys(currentPositions).forEach(joint => {
        const slider = document.getElementById(`servo-${joint}`);
        const angleDisplay = document.getElementById(`angle-${joint}`);
        
        if (slider && angleDisplay) {
            slider.value = currentPositions[joint];
            angleDisplay.textContent = currentPositions[joint] + '°';
        }
    });
}

// Arm-Status anzeigen
function updateArmStatusDisplay() {
    if (!armInfo) return;
    
    const statusHtml = `
        <div class="row text-center">
            <div class="col-6">
                <div class="card bg-light">
                    <div class="card-body">
                        <h6>Controller</h6>
                        <span class="badge ${armInfo.controller.hardware_available ? 'bg-success' : 'bg-warning'}">
                            ${armInfo.controller.hardware_available ? 'Hardware' : 'Mock'}
                        </span>
                    </div>
                </div>
            </div>
            <div class="col-6">
                <div class="card bg-light">
                    <div class="card-body">
                        <h6>Servos</h6>
                        <span class="badge bg-info">${armInfo.controller.servo_count}</span>
                    </div>
                </div>
            </div>
        </div>
        <div class="mt-3">
            <strong>I2C Adresse:</strong> ${armInfo.controller.i2c_address}<br>
            <strong>Frequenz:</strong> ${armInfo.controller.frequency}Hz<br>
            <strong>Gelenke:</strong> ${armInfo.joints.join(', ')}<br>
            <strong>Presets:</strong> ${armInfo.presets.join(', ')}
        </div>
    `;
    
    document.getElementById('arm-status').innerHTML = statusHtml;
}

// Unkraut-Entfernung Sequenz
function startWeedRemovalSequence() {
    logActivity('🌿 Starte Unkraut-Entfernung Sequenz...');
    
    fetch('/api/arm/weed_removal', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({target_x: 0, target_y: 0})
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'sequence_started') {
            logActivity('✅ Unkraut-Entfernung Sequenz gestartet');
        } else {
            logActivity(`❌ Sequenz-Start fehlgeschlagen: ${data.error}`);
        }
    })
    .catch(error => {
        console.error('Sequenz-Fehler:', error);
        logActivity(`❌ Sequenz-Fehler: ${error}`);
    });
}

// Werkzeug aktivieren
function activateTool() {
    logActivity('🔧 Aktiviere Werkzeug...');
    
    fetch('/api/arm/tool/activate', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({duration: 3.0})
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'tool_activated') {
            logActivity('✅ Werkzeug aktiviert (3 Sekunden)');
        } else {
            logActivity(`❌ Werkzeug-Aktivierung fehlgeschlagen: ${data.error}`);
        }
    })
    .catch(error => {
        console.error('Werkzeug-Fehler:', error);
        logActivity(`❌ Werkzeug-Fehler: ${error}`);
    });
}

// Servo-Kalibrierung
function calibrateServos() {
    logActivity('🔧 Starte Servo-Kalibrierung...');
    
    fetch('/api/arm/calibrate', {method: 'POST'})
        .then(response => response.json())
        .then(data => {
            if (data.status === 'calibration_started') {
                logActivity('✅ Servo-Kalibrierung gestartet');
            } else {
                logActivity(`❌ Kalibrierung fehlgeschlagen: ${data.error}`);
            }
        })
        .catch(error => {
            console.error('Kalibrierung-Fehler:', error);
            logActivity(`❌ Kalibrierung-Fehler: ${error}`);
        });
}

// Not-Stopp
function emergencyStop() {
    logActivity('🚨 ROBOTERARM NOT-STOPP');
    
    fetch('/api/arm/emergency_stop', {method: 'POST'})
        .then(response => response.json())
        .then(data => {
            logActivity('🛑 Not-Stopp aktiviert');
        })
        .catch(error => {
            console.error('Not-Stopp Fehler:', error);
            logActivity(`❌ Not-Stopp Fehler: ${error}`);
        });
}

// Alle Servos zurücksetzen
function resetAllServos() {
    moveToPreset('home');
}

// Aktivitätslog
function logActivity(message) {
    const log = document.getElementById('activity-log');
    const timestamp = new Date().toLocaleTimeString();
    const entry = document.createElement('div');
    entry.innerHTML = `<span class="text-muted">[${timestamp}]</span> ${message}`;
    log.appendChild(entry);
    log.scrollTop = log.scrollHeight;
}

function clearLog() {
    document.getElementById('activity-log').innerHTML = 
        '<div class="text-muted">Roboterarm-Aktivitäten werden hier angezeigt...</div>';
}

// Keyboard-Shortcuts
document.addEventListener('keydown', function(e) {
    if (e.ctrlKey) {
        switch(e.code) {
            case 'KeyH':
                e.preventDefault();
                moveToPreset('home');
                break;
            case 'KeyP':
                e.preventDefault();
                moveToPreset('park');
                break;
            case 'KeyS':
                e.preventDefault();
                emergencyStop();
                break;
        }
    }
});
</script>
{% endblock %}
'''