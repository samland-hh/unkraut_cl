// app/static/js/camera-tools.js
/**
 * Erweiterte Kamera-Tools für Unkraut-2025
 * Bulk-Tagging, Cleanup, Export, Statistiken
 */

class CameraTools {
    constructor() {
        // Automatische Initialisierung
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.init());
        } else {
            this.init();
        }
    }
    
    init() {
        console.log('🔧 Initialisiere Kamera-Tools...');
        
        this.bindEventListeners();
        this.startStatsUpdates();
        
        console.log('✅ Kamera-Tools bereit');
    }
    
    bindEventListeners() {
        // Tool-Aktionen
        document.querySelectorAll('[data-tool-action]').forEach(btn => {
            const action = btn.dataset.toolAction;
            btn.addEventListener('click', (e) => this.handleToolAction(action, e));
        });
        
        console.log('📎 Tool Event-Listener gebunden');
    }
    
    async handleToolAction(action, event) {
        const button = event.target;
        this.setButtonLoading(button, true);
        
        try {
            switch(action) {
                case 'bulk-tag':
                    await this.quickBulkTag();
                    break;
                case 'preview-cleanup':
                    await this.previewCleanup();
                    break;
                case 'execute-cleanup':
                    await this.executeCleanup();
                    break;
                case 'start-export':
                    await this.startExport();
                    break;
                case 'export-stats':
                    this.exportStats();
                    break;
                case 'reset-stats':
                    this.resetStats();
                    break;
                default:
                    console.warn(`Unbekannte Tool-Aktion: ${action}`);
            }
        } catch (error) {
            console.error(`Fehler bei Tool-Aktion ${action}:`, error);
            this.showNotification(`❌ Fehler: ${error.message}`, 'error');
        } finally {
            this.setButtonLoading(button, false);
        }
    }
    
    async quickBulkTag() {
        const tagInput = document.getElementById('bulk-tag-input');
        const tag = tagInput.value.trim();
        
        if (!tag) {
            this.showNotification('❌ Bitte Tag eingeben', 'warning');
            return;
        }
        
        if (!window.enhancedImageGallery || window.enhancedImageGallery.selectedImages.size === 0) {
            this.showNotification('❌ Keine Bilder ausgewählt. Aktiviere Bulk-Modus und wähle Bilder aus.', 'warning');
            return;
        }
        
        try {
            // Verwende die Tag-Funktion der Galerie
            const selectedList = Array.from(window.enhancedImageGallery.selectedImages);
            
            this.showNotification(`🏷️ Tagge ${selectedList.length} Bilder mit "${tag}"...`, 'info');
            
            const response = await fetch('/api/gallery/tag-images', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ files: selectedList, tag: tag })
            });
            
            const result = await response.json();
            
            if (response.ok) {
                this.showNotification(`✅ ${result.tagged} Bilder mit "${tag}" getaggt`, 'success');
                tagInput.value = '';
            } else {
                throw new Error(result.error || 'Tagging fehlgeschlagen');
            }
            
        } catch (error) {
            console.error('Quick-Tag-Fehler:', error);
            this.showNotification(`❌ Tagging fehlgeschlagen: ${error.message}`, 'error');
        }
    }
    
    async previewCleanup() {
        const preset = document.getElementById('cleanup-preset').value;
        const settings = this.getCleanupSettings(preset);
        
        try {
            this.showNotification('🔍 Analysiere Dateien für Cleanup...', 'info');
            
            const response = await fetch('/api/gallery/cleanup', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({...settings, dry_run: true})
            });
            
            const result = await response.json();
            
            if (response.ok) {
                const totalSize = result.candidates.reduce((sum, c) => sum + c.size, 0);
                const reasons = result.candidates.reduce((acc, c) => {
                    acc[c.reason] = (acc[c.reason] || 0) + 1;
                    return acc;
                }, {});
                
                let reasonText = '';
                for (const [reason, count] of Object.entries(reasons)) {
                    reasonText += `${reason}: ${count} Dateien\n`;
                }
                
                const message = `📋 Cleanup-Vorschau (${preset}):\n\n` +
                    `${result.candidate_count} Dateien würden gelöscht\n` +
                    `Freigegebener Speicher: ${this.formatFileSize(totalSize)}\n\n` +
                    `Gründe:\n${reasonText}`;
                
                alert(message); // Einfacher Alert für Vorschau
                
            } else {
                throw new Error(result.error || 'Cleanup-Vorschau fehlgeschlagen');
            }
            
        } catch (error) {
            console.error('Cleanup-Preview-Fehler:', error);
            this.showNotification(`❌ Cleanup-Vorschau fehlgeschlagen: ${error.message}`, 'error');
        }
    }
    
    async executeCleanup() {
        const preset = document.getElementById('cleanup-preset').value;
        const settings = this.getCleanupSettings(preset);
        
        const confirmed = confirm(`🗑️ Cleanup mit "${preset}" Einstellungen ausführen?\n\nDieser Vorgang kann nicht rückgängig gemacht werden!`);
        if (!confirmed) return;
        
        try {
            this.showNotification('🧹 Führe Cleanup durch...', 'info');
            
            const response = await fetch('/api/gallery/cleanup', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({...settings, dry_run: false})
            });
            
            const result = await response.json();
            
            if (response.ok) {
                this.showNotification(
                    `✅ Cleanup abgeschlossen: ${result.deleted_count} Dateien gelöscht, ${this.formatFileSize(result.freed_space)} freigegeben`, 
                    'success'
                );
                
                // Galerie neu laden
                if (window.enhancedImageGallery) {
                    setTimeout(() => window.enhancedImageGallery.loadGallery(), 1000);
                }
                
                // Statistiken aktualisieren
                setTimeout(() => this.updateGalleryStats(), 1500);
                
            } else {
                throw new Error(result.error || 'Cleanup fehlgeschlagen');
            }
            
        } catch (error) {
            console.error('Cleanup-Fehler:', error);
            this.showNotification(`❌ Cleanup fehlgeschlagen: ${error.message}`, 'error');
        }
    }
    
    async startExport() {
        const format = document.getElementById('export-format').value;
        
        try {
            this.showNotification(`📤 Export "${format}" wird vorbereitet...`, 'info');
            
            switch(format) {
                case 'original':
                    if (window.enhancedImageGallery) {
                        await window.enhancedImageGallery.downloadImages();
                    } else {
                        // Fallback für normale Galerie
                        const response = await fetch('/api/gallery/download', { method: 'POST' });
                        if (response.ok) {
                            const blob = await response.blob();
                            this.downloadBlob(blob, 'alle_bilder_original.zip');
                        }
                    }
                    break;
                    
                case 'web':
                    this.showNotification('🌐 Web-Export: Komprimierte Versionen für Web-Nutzung', 'info');
                    // TODO: Implementierung für Web-optimierte Bilder
                    setTimeout(() => {
                        this.showNotification('⚠️ Web-Export noch nicht implementiert', 'warning');
                    }, 1000);
                    break;
                    
                case 'ai-training':
                    this.showNotification('🧠 KI-Training-Export: Sammle getaggte Bilder...', 'info');
                    // TODO: Implementierung für KI-Training-Set
                    setTimeout(() => {
                        this.showNotification('⚠️ KI-Training-Export noch nicht implementiert', 'warning');
                    }, 1000);
                    break;
                    
                default:
                    throw new Error(`Unbekanntes Export-Format: ${format}`);
            }
            
        } catch (error) {
            console.error('Export-Fehler:', error);
            this.showNotification(`❌ Export fehlgeschlagen: ${error.message}`, 'error');
        }
    }
    
    exportStats() {
        try {
            // Sammle alle verfügbaren Statistiken
            const stats = {
                timestamp: new Date().toISOString(),
                camera_settings: JSON.parse(localStorage.getItem('cameraSettings') || '{}'),
                total_captures: localStorage.getItem('totalCaptures') || '0',
                galerie_stats: this.getGalleryStatsFromDOM(),
                system_info: {
                    user_agent: navigator.userAgent,
                    screen_resolution: `${screen.width}x${screen.height}`,
                    viewport: `${window.innerWidth}x${window.innerHeight}`
                }
            };
            
            // Als JSON-Datei herunterladen
            const jsonString = JSON.stringify(stats, null, 2);
            const blob = new Blob([jsonString], { type: 'application/json' });
            this.downloadBlob(blob, `kamera_statistiken_${new Date().toISOString().slice(0,10)}.json`);
            
            this.showNotification('📊 Statistiken als JSON exportiert', 'success');
            
        } catch (error) {
            console.error('Stats-Export-Fehler:', error);
            this.showNotification('❌ Statistik-Export fehlgeschlagen', 'error');
        }
    }
    
    resetStats() {
        const confirmed = confirm('🔄 Alle Kamera-Statistiken zurücksetzen?\n\nDies löscht gespeicherte Einstellungen und Zähler.');
        
        if (confirmed) {
            try {
                // Lösche alle relevanten localStorage-Einträge
                localStorage.removeItem('cameraSettings');
                localStorage.removeItem('totalCaptures');
                localStorage.removeItem('lastCaptureTime');
                localStorage.removeItem('sessionStats');
                
                this.showNotification('🔄 Alle Statistiken zurückgesetzt', 'success');
                
                // Aktualisiere UI-Elemente
                if (window.cameraController) {
                    window.cameraController.updateCameraStats();
                }
                
                setTimeout(() => this.updateGalleryStats(), 500);
                
            } catch (error) {
                console.error('Stats-Reset-Fehler:', error);
                this.showNotification('❌ Reset fehlgeschlagen', 'error');
            }
        }
    }
    
    getCleanupSettings(preset) {
        const settings = {
            conservative: { days_old: 30, max_size_mb: 10, keep_tagged: true },
            moderate: { days_old: 14, max_size_mb: 5, keep_tagged: true },
            aggressive: { days_old: 7, max_size_mb: 2, keep_tagged: false }
        };
        
        return settings[preset] || settings.conservative;
    }
    
    async updateGalleryStats() {
        try {
            const response = await fetch('/api/gallery/stats');
            const stats = await response.json();
            
            if (response.ok) {
                // Update DOM-Elemente
                const elements = {
                    'total-images': stats.total_images,
                    'total-size': this.formatFileSize(stats.total_size),
                    'today-count': stats.today_count,
                    'tag-count': stats.tag_count
                };
                
                for (const [id, value] of Object.entries(elements)) {
                    const element = document.getElementById(id);
                    if (element) {
                        element.textContent = value;
                    }
                }
                
                console.log('📊 Galerie-Statistiken aktualisiert');
                
            } else {
                console.warn('Statistik-API-Fehler:', stats.error);
            }
            
        } catch (error) {
            console.error('Stats-Update-Fehler:', error);
            
            // Fallback: Setze Platzhalter
            ['total-images', 'total-size', 'today-count', 'tag-count'].forEach(id => {
                const element = document.getElementById(id);
                if (element) element.textContent = '❌';
            });
        }
    }
    
    getGalleryStatsFromDOM() {
        return {
            total_images: document.getElementById('total-images')?.textContent || '0',
            total_size: document.getElementById('total-size')?.textContent || '0 B',
            today_count: document.getElementById('today-count')?.textContent || '0',
            tag_count: document.getElementById('tag-count')?.textContent || '0'
        };
    }
    
    downloadBlob(blob, filename) {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    }
    
    formatFileSize(bytes) {
        if (!bytes) return '0 B';
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    }
    
    setButtonLoading(button, loading) {
        if (loading) {
            button.dataset.loading = 'true';
            button.disabled = true;
        } else {
            delete button.dataset.loading;
            button.disabled = false;
        }
    }
    
    showNotification(message, type = 'info') {
        // Nutze globale Notification-Funktion falls verfügbar
        if (window.showNotification) {
            window.showNotification(message, type);
        } else {
            // Fallback
            console.log(`${type.toUpperCase()}: ${message}`);
        }
    }
    
    startStatsUpdates() {
        // Initiales Stats-Update
        setTimeout(() => this.updateGalleryStats(), 2000);
        
        // Auto-Update alle 30 Sekunden
        setInterval(() => {
            this.updateGalleryStats();
        }, 30000);
    }
}

// Automatische Initialisierung
const cameraTools = new CameraTools();

// Für Debugging
window.cameraTools = cameraTools;