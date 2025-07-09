// app/static/js/debug_logging.js
// Debug-System: Browser Events -> Python Terminal

class TerminalLogger {
    constructor() {
        this.enabled = true;
        this.logQueue = [];
        this.isProcessing = false;
        this.sessionId = this.generateSessionId();
        
        this.init();
    }
    
    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
    
    init() {
        console.log('🔍 Terminal Debug Logger initialisiert');
        this.log('🚀 Debug Session gestartet', 'INFO', 'BROWSER', {
            sessionId: this.sessionId,
            userAgent: navigator.userAgent,
            viewport: `${window.innerWidth}x${window.innerHeight}`,
            touch: 'ontouchstart' in window,
            url: window.location.href
        });
        
        // Error-Handler
        window.addEventListener('error', (e) => {
            this.log(`💥 JavaScript Fehler: ${e.message}`, 'ERROR', 'JS_ERROR', {
                filename: e.filename,
                line: e.lineno,
                column: e.colno,
                stack: e.error ? e.error.stack : 'Kein Stack verfügbar'
            });
        });
        
        // Unhandled Promise Rejections
        window.addEventListener('unhandledrejection', (e) => {
            this.log(`💥 Unhandled Promise Rejection: ${e.reason}`, 'ERROR', 'PROMISE', {
                reason: e.reason
            });
        });
    }
    
    async log(message, level = 'INFO', source = 'BROWSER', extra = {}) {
        if (!this.enabled) return;
        
        const logEntry = {
            message: message,
            level: level,
            source: source,
            extra: {
                ...extra,
                sessionId: this.sessionId,
                timestamp: Date.now(),
                url: window.location.pathname
            }
        };
        
        // Auch lokal loggen
        const color = this.getLevelColor(level);
        console.log(`%c[${level}] ${message}`, `color: ${color}`, extra);
        
        // An Python Terminal senden
        this.logQueue.push(logEntry);
        this.processQueue();
    }
    
    getLevelColor(level) {
        const colors = {
            'INFO': '#2196F3',
            'TOUCH': '#FF9800', 
            'ERROR': '#F44336',
            'SUCCESS': '#4CAF50',
            'MOBILE': '#9C27B0',
            'CAMERA': '#3F51B5'
        };
        return colors[level] || '#666';
    }
    
    async processQueue() {
        if (this.isProcessing || this.logQueue.length === 0) return;
        
        this.isProcessing = true;
        
        try {
            while (this.logQueue.length > 0) {
                const logEntry = this.logQueue.shift();
                
                try {
                    await fetch('/api/debug/log', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify(logEntry)
                    });
                } catch (error) {
                    // Stumm bei Network-Fehlern um Loops zu vermeiden
                    console.warn('Debug-Log failed:', error);
                }
            }
        } finally {
            this.isProcessing = false;
        }
    }
    
    // Touch-Event spezielle Logging
    async logTouch(eventType, element, coordinates = null) {
        const touchData = {
            type: eventType,
            element: this.getElementDescription(element),
            coordinates: coordinates,
            timestamp: Date.now()
        };
        
        this.log(`👆 Touch ${eventType}: ${touchData.element}`, 'TOUCH', 'MOBILE');
        
        // Spezielle Touch-API
        try {
            await fetch('/api/debug/touch', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(touchData)
            });
        } catch (error) {
            console.warn('Touch-Log failed:', error);
        }
    }
    
    getElementDescription(element) {
        if (!element) return 'unknown';
        
        const tag = element.tagName.toLowerCase();
        const id = element.id ? `#${element.id}` : '';
        const classes = element.className ? `.${element.className.split(' ').join('.')}` : '';
        const text = element.textContent ? element.textContent.substring(0, 30) : '';
        
        return `${tag}${id}${classes} "${text}"`;
    }
    
    // Fetch-Wrapper mit Logging
    async loggedFetch(url, options = {}) {
        const startTime = Date.now();
        
        this.log(`🌐 API Request: ${options.method || 'GET'} ${url}`, 'INFO', 'API', {
            method: options.method || 'GET',
            headers: options.headers,
            hasBody: !!options.body
        });
        
        try {
            const response = await fetch(url, options);
            const duration = Date.now() - startTime;
            
            if (response.ok) {
                this.log(`✅ API Success: ${response.status} ${url} (${duration}ms)`, 'SUCCESS', 'API');
            } else {
                this.log(`❌ API Error: ${response.status} ${url} (${duration}ms)`, 'ERROR', 'API', {
                    status: response.status,
                    statusText: response.statusText
                });
            }
            
            return response;
            
        } catch (error) {
            const duration = Date.now() - startTime;
            this.log(`💥 API Network Error: ${url} (${duration}ms)`, 'ERROR', 'API', {
                error: error.message
            });
            throw error;
        }
    }
}

// Global Logger Instance
window.terminalLogger = new TerminalLogger();

// Touch-Event Monitoring für alle Buttons
function setupTouchLogging() {
    terminalLogger.log('🔧 Touch-Event Logging wird eingerichtet...', 'INFO', 'SETUP');
    
    // Alle Buttons überwachen
    document.addEventListener('DOMContentLoaded', function() {
        setTimeout(() => {
            const buttons = document.querySelectorAll('button, .btn, [onclick]');
            
            terminalLogger.log(`📱 ${buttons.length} Touch-fähige Elemente gefunden`, 'INFO', 'SETUP');
            
            buttons.forEach((btn, index) => {
                const description = terminalLogger.getElementDescription(btn);
                
                // Touch Events
                btn.addEventListener('touchstart', function(e) {
                    const touch = e.touches[0];
                    const coordinates = touch ? {x: Math.round(touch.clientX), y: Math.round(touch.clientY)} : null;
                    
                    terminalLogger.logTouch('touchstart', this, coordinates);
                    
                    // Spezielle Behandlung für Foto-Button
                    if (description.includes('📸') || description.includes('foto') || description.includes('capture')) {
                        terminalLogger.log('📸 FOTO-BUTTON TOUCHED!', 'CAMERA', 'MOBILE', {
                            buttonText: this.textContent,
                            coordinates: coordinates
                        });
                    }
                }, {passive: true});
                
                btn.addEventListener('touchend', function(e) {
                    terminalLogger.logTouch('touchend', this);
                }, {passive: true});
                
                // Click Events (für Desktop/Fallback)
                btn.addEventListener('click', function(e) {
                    terminalLogger.log(`🖱️ Click: ${description}`, 'INFO', 'DESKTOP');
                }, {passive: true});
            });
            
            terminalLogger.log('✅ Touch-Event Logging aktiv für alle Buttons', 'SUCCESS', 'SETUP');
        }, 1000);
    });
}

// Original Funktionen überschreiben für Logging
function wrapCameraFunctions() {
    // captureImage überschreiben
    if (typeof window.captureImage === 'function') {
        const originalCaptureImage = window.captureImage;
        window.captureImage = function() {
            terminalLogger.log('📸 captureImage() aufgerufen', 'CAMERA', 'FUNCTION');
            return originalCaptureImage.apply(this, arguments);
        };
    }
    
    // fetch überschreiben für automatisches Logging
    const originalFetch = window.fetch;
    window.fetch = function(url, options = {}) {
        // Nur API-Calls loggen, nicht Debug-Logs selbst
        if (typeof url === 'string' && url.includes('/api/') && !url.includes('/debug/')) {
            return terminalLogger.loggedFetch(url, options);
        }
        return originalFetch(url, options);
    };
    
    terminalLogger.log('🔧 Kamera-Funktionen für Logging überschrieben', 'INFO', 'SETUP');
}

// Mobile-spezifische Logs
function logMobileInfo() {
    const isMobile = /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    const hasTouch = 'ontouchstart' in window;
    const isStandalone = window.navigator.standalone === true;
    
    terminalLogger.log('📱 Mobile-Gerät Info:', 'MOBILE', 'DEVICE', {
        isMobile: isMobile,
        hasTouch: hasTouch,
        isStandalone: isStandalone,
        orientation: screen.orientation ? screen.orientation.type : 'unknown',
        maxTouchPoints: navigator.maxTouchPoints || 0,
        pixelRatio: window.devicePixelRatio
    });
}

// Initialization
document.addEventListener('DOMContentLoaded', function() {
    terminalLogger.log('📄 DOM Content Loaded', 'INFO', 'DOM');
    
    logMobileInfo();
    setupTouchLogging();
    wrapCameraFunctions();
    
    // Test der Debug-Verbindung
    terminalLogger.log('🧪 Terminal Debug System bereit', 'SUCCESS', 'READY', {
        page: window.location.pathname,
        timestamp: new Date().toISOString()
    });
});

// Export für andere Module
window.debugLog = (message, level, source, extra) => {
    terminalLogger.log(message, level, source, extra);
};

// Periodische Heartbeat-Logs
setInterval(() => {
    terminalLogger.log('💓 Heartbeat', 'INFO', 'SYSTEM', {
        memory: performance.memory ? Math.round(performance.memory.usedJSHeapSize / 1024 / 1024) + 'MB' : 'unknown',
        connections: navigator.onLine ? 'online' : 'offline'
    });
}, 30000); // Alle 30 Sekunden