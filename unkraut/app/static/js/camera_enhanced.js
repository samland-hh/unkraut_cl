// unkraut/app/static/js/camera_enhanced.js - KORRIGIERT

/**
 * KORRIGIERTE Mobile-kompatible Version - const-Fehler behoben
 * Verwendet Promise.then() für bessere Browser-Kompatibilität
 */

// Globale Variablen
var continuousDetectionActive = false;
var galleryImages = [];
var statsUpdateInterval = null;

// Klasse für Camera Controller
function CameraController() {
    this.isInitialized = false;
    this.init();
}

CameraController.prototype.init = function() {
    this.bindEventListeners();
    this.setupAutoUpdates();
    this.isInitialized = true;
    console.log('📹 KORRIGIERTE Mobile Camera Controller initialisiert');
};

CameraController.prototype.bindEventListeners = function() {
    var self = this;
    
    // Auto-Load beim Seitenstart
    document.addEventListener('DOMContentLoaded', function() {
        self.updateCameraStats();
        self.loadImageGallery();
    });
    
    // Stream Error Handling
    var streamImg = document.getElementById('camera-stream');
    if (streamImg) {
        streamImg.addEventListener('error', function() {
            console.warn('❌ Kamera-Stream Fehler');
            self.showNotification('❌ Stream-Verbindung unterbrochen', 'error');
        });
        
        streamImg.addEventListener('load', function() {
            console.log('📹 Kamera-Stream aktiv');
        });
    }
};

CameraController.prototype.setupAutoUpdates = function() {
    var self = this;
    
    // Auto-Update Stats alle 10 Sekunden
    if (statsUpdateInterval) {
        clearInterval(statsUpdateInterval);
    }
    
    statsUpdateInterval = setInterval(function() {
        self.updateCameraStats();
    }, 10000);
    
    console.log('📊 Auto-Update Stats gestartet (10s Intervall)');
};

CameraController.prototype.updateCameraStats = function() {
    var self = this;
    console.log('📊 DEBUG: updateCameraStats gestartet');
    
    fetch('/api/system/status')
        .then(function(response) {
            console.log('📊 DEBUG: Response Status:', response.status);
            return response.json();
        })
        .then(function(data) {
            console.log('📊 DEBUG: Response Data:', data);
            
            // System-Stats aktualisieren
            self.updateElement('cpu-usage', data.system.cpu_usage + '%');
            self.updateElement('ram-usage', data.system.memory_usage + '%');
            self.updateElement('cpu-temp', data.system.cpu_temperature + '°C');
            
            // Hardware-Status
            self.updateElement('camera-status', 
                data.hardware.camera_available ? 'Online' : 'Offline');
            self.updateElement('arm-status', 
                data.hardware.arm_available ? 'Verfügbar' : 'Mock');
            self.updateElement('stream-fps', '30 FPS');
            
            console.log('📊 Kamera-Statistiken aktualisiert');
        })
        .catch(function(error) {
            console.error('❌ Stats-Update-Fehler:', error);
            // Fallback-Werte setzen
            self.updateElement('cpu-usage', 'N/A');
            self.updateElement('ram-usage', 'N/A');
            self.updateElement('cpu-temp', 'N/A');
            self.updateElement('camera-status', 'Unbekannt');
            self.updateElement('arm-status', 'Unbekannt');
        });
};

CameraController.prototype.updateElement = function(id, content) {
    var element = document.getElementById(id);
    if (element) {
        element.textContent = content;
    }
};

CameraController.prototype.captureImage = function() {
    var self = this;
    console.log('📸 DEBUG: captureImage() gestartet');
    
    try {
        this.showNotification('📸 Nehme Foto auf...', 'info');
        
        // Timestamp generieren - KORREKT mit let/var
        var now = new Date();
        var yy = String(now.getFullYear()).slice(-2);
        var mm = String(now.getMonth() + 1);
        var dd = String(now.getDate());
        var hh = String(now.getHours());
        var min = String(now.getMinutes());
        var ss = String(now.getSeconds());
        
        // Padding hinzufügen
        if (mm.length === 1) mm = '0' + mm;
        if (dd.length === 1) dd = '0' + dd;
        if (hh.length === 1) hh = '0' + hh;
        if (min.length === 1) min = '0' + min;
        if (ss.length === 1) ss = '0' + ss;
        
        var timestamp = yy + '.' + mm + '.' + dd + '_' + hh + '.' + min + '_' + ss;
        var customFilename = 'img_' + timestamp + '.jpg';
        
        console.log('📸 DEBUG: Filename:', customFilename);
        
        // API-Request mit Promise.then()
        console.log('📸 DEBUG: Sende Request...');
        
        fetch('/api/camera/capture', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                filename: customFilename
            })
        })
        .then(function(response) {
            console.log('📸 DEBUG: Response Status:', response.status);
            return response.json();
        })
        .then(function(data) {
            console.log('📸 DEBUG: Response Data:', data);
            
            if (data.filename) {
                self.showNotification('📸 Foto gespeichert: ' + data.filename, 'success');
                
                // Galerie nach 1 Sekunde aktualisieren
                setTimeout(function() {
                    self.loadImageGallery();
                }, 1000);
            } else {
                console.error('❌ DEBUG: Kein Filename in Response');
                self.showNotification('❌ Foto-Aufnahme fehlgeschlagen', 'error');
            }
        })
        .catch(function(error) {
            console.error('❌ DEBUG: Capture-Fehler:', error);
            self.showNotification('❌ Kamera-Fehler: ' + error.message, 'error');
        });
        
    } catch (error) {
        console.error('❌ DEBUG: JavaScript-Fehler:', error);
        this.showNotification('❌ JavaScript-Fehler: ' + error.message, 'error');
    }
};

CameraController.prototype.loadImageGallery = function() {
    var self = this;
    console.log('📁 DEBUG: loadImageGallery() gestartet');
    
    fetch('/api/camera/images')
        .then(function(response) {
            return response.json();
        })
        .then(function(data) {
            console.log('📁 DEBUG: Galerie-Daten:', data);
            
            galleryImages = data.images || [];
            self.renderGallery();
            
            // Stats aktualisieren
            self.updateElement('gallery-count', galleryImages.length + ' Bilder');
            self.updateElement('gallery-size', (data.total_size_mb || 0).toFixed(1) + ' MB');
        })
        .catch(function(error) {
            console.error('❌ Galerie-Laden-Fehler:', error);
            self.showNotification('❌ Galerie konnte nicht geladen werden', 'error');
        });
};

CameraController.prototype.renderGallery = function() {
    var gallery = document.getElementById('image-gallery');
    if (!gallery) return;
    
    if (galleryImages.length === 0) {
        gallery.innerHTML = '<div class="no-images">Keine Bilder aufgenommen</div>';
        return;
    }
    
    // Gallery HTML erstellen
    var galleryHTML = '';
    for (var i = 0; i < galleryImages.length; i++) {
        var image = galleryImages[i];
        galleryHTML += '<div class="gallery-item">';
        galleryHTML += '  <div class="gallery-image-container">';
        galleryHTML += '    <img src="/api/camera/image/' + image.filename + '"';
        galleryHTML += '         alt="' + image.filename + '"';
        galleryHTML += '         class="gallery-image"';
        galleryHTML += '         onclick="cameraController.openImageModal(\'' + image.filename + '\')">';
        galleryHTML += '    <button class="delete-cross"';
        galleryHTML += '            onclick="event.stopPropagation(); cameraController.deleteImage(\'' + image.filename + '\')"';
        galleryHTML += '            title="Bild löschen">';
        galleryHTML += '    </button>';
        galleryHTML += '  </div>';
        galleryHTML += '  <div class="image-info">';
        galleryHTML += '    <div class="image-filename">' + image.filename + '</div>';
        galleryHTML += '  </div>';
        galleryHTML += '</div>';
    }
    
    gallery.innerHTML = galleryHTML;
};

CameraController.prototype.deleteImage = function(filename) {
    var self = this;
    
    if (!confirm('Bild "' + filename + '" wirklich löschen?')) return;
    
    fetch('/api/camera/image/' + filename, {
        method: 'DELETE'
    })
    .then(function(response) {
        if (response.ok) {
            self.showNotification('🗑️ Bild "' + filename + '" gelöscht', 'success');
            self.loadImageGallery();
        } else {
            self.showNotification('❌ Löschen fehlgeschlagen', 'error');
        }
    })
    .catch(function(error) {
        console.error('❌ Delete-Fehler:', error);
        self.showNotification('❌ Löschen fehlgeschlagen', 'error');
    });
};

CameraController.prototype.showNotification = function(message, type) {
    // Bestehende Notifications entfernen
    var existingNotifications = document.querySelectorAll('.notification');
    for (var i = 0; i < existingNotifications.length; i++) {
        existingNotifications[i].remove();
    }
    
    // Neue Notification erstellen
    var notification = document.createElement('div');
    notification.className = 'notification ' + type;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Auto-Remove nach 3 Sekunden
    setTimeout(function() {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 3000);
    
    console.log(type.toUpperCase() + ': ' + message);
};

CameraController.prototype.openImageModal = function(filename) {
    window.open('/api/camera/image/' + filename, '_blank');
};

// Globale Instanz erstellen
console.log('📱 DEBUG: Erstelle KORRIGIERTE CameraController...');
var cameraController = new CameraController();

// Globale Funktionen für onclick-Handler
function captureImage() {
    console.log('📱 DEBUG: Globale captureImage() aufgerufen');
    cameraController.captureImage();
}

function updateCameraStats() {
    cameraController.updateCameraStats();
}

function loadImageGallery() {
    cameraController.loadImageGallery();
}

// Weitere Funktionen...
function detectWeeds() {
    console.log('🔍 DEBUG: detectWeeds() - Mock');
    cameraController.showNotification('🔍 Mock-Erkennung', 'info');
}

function continuousDetection() {
    console.log('📹 DEBUG: continuousDetection() - Mock');
    cameraController.showNotification('📹 Mock-Kontinuierliche-Erkennung', 'info');
}

function clearResults() {
    console.log('🗑️ DEBUG: clearResults() - Mock');
}

function toggleStream() {
    console.log('📹 DEBUG: toggleStream() - Mock');
}

function downloadImages() {
    window.open('/api/camera/download_all', '_blank');
}

function clearImages() {
    if (confirm('Wirklich ALLE Bilder löschen?')) {
        fetch('/api/camera/images/clear', {method: 'POST'})
        .then(function(response) {
            if (response.ok) {
                cameraController.showNotification('🗑️ Alle Bilder gelöscht', 'success');
                cameraController.loadImageGallery();
            }
        });
    }
}

//console.log('📱 KORRIGIERTE Camera JavaScript geladen!');