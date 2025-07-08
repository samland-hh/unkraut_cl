// unkraut/app/static/js/camera-init.js

/**
 * Template-spezifische Initialisierung für Kamera-Seite
 * Lädt nach dem DOM und camera.js
 */

// Zusätzliche Template-spezifische Funktionen
function downloadStats() {
    const statsElement = document.getElementById('camera-stats');
    if (statsElement) {
        const stats = statsElement.textContent;
        const blob = new Blob([stats], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `kamera_statistiken_${new Date().toISOString().split('T')[0]}.txt`;
        a.click();
        URL.revokeObjectURL(url);
        
        if (window.showNotification) {
            showNotification('📊 Statistiken exportiert', 'success');
        }
    }
}

// Template-Initialisierung
document.addEventListener('DOMContentLoaded', function() {
    console.log('📷 Kamera-Template wird initialisiert...');
    
    // Prüfe alle notwendigen Elemente
    const requiredElements = [
        'camera-stream',
        'camera-stats', 
        'detection-results',
        'image-gallery'
    ];
    
    let missingElements = [];
    requiredElements.forEach(id => {
        if (!document.getElementById(id)) {
            missingElements.push(id);
        }
    });
    
    if (missingElements.length > 0) {
        console.error('❌ Fehlende Template-Elemente:', missingElements);
    } else {
        console.log('✅ Alle Template-Elemente gefunden');
    }
    
    // Setze initiale Stream-URL mit Cache-Busting
    const cameraStream = document.getElementById('camera-stream');
    if (cameraStream) {
        const streamUrl = '/api/camera/stream?' + Date.now();
        cameraStream.src = streamUrl;
        
        // Error-Handling für Stream
        cameraStream.onerror = function() {
            console.log('⚠️ Stream-Fehler, verwende Fallback');
            this.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjQwIiBoZWlnaHQ9IjQ4MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KICA8cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjMjEyMTIxIi8+CiAgPHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCwgc2Fucy1zZXJpZiIgZm9udC1zaXplPSIyNHB4IiBmaWxsPSIjNjY2IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkeT0iLjNlbSI+S2FtZXJhIG5pY2h0IHZlcmbDvGdiYXI8L3RleHQ+Cjwvc3ZnPg==';
        };
        
        // Success-Handling
        cameraStream.onload = function() {
            console.log('✅ Kamera-Stream geladen');
        };
    }
    
    // Prüfe JSZip-Verfügbarkeit
    if (typeof JSZip === 'undefined') {
        console.warn('⚠️ JSZip nicht verfügbar - Download-Feature eingeschränkt');
    }
    
    console.log('✅ Kamera-Template initialisiert');
});

// Export zusätzlicher Funktionen
window.downloadStats = downloadStats;