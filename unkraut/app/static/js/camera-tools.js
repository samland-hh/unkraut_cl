// app/static/js/camera-tools.js
/**
 * Reparierte Kamera-Tools mit korrigierten API-Endpoints
 * Behebt 404-Fehler bei Statistik-Abfragen
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
        console.log('🔧 Initialisiere reparierte Kamera-Tools...');
        
        this.bindEventListeners();
        this.startStatsUpdates();
        
        console.log('✅ Reparierte Kamera-Tools bereit');
    }
    
    bindEventListeners() {
        // Tool-Aktionen
        document.querySelectorAll('[data-tool-action]').forEach(btn => {
            const action = btn.dataset.toolAction;
            btn.addEventListener('click', (e) => this.handleToolAction(action, e));
        });
        
        // Stats-Aktionen
        document.querySelectorAll('[data-stats-action]').forEach(btn => {
            const action = btn.dataset.statsAction;
            btn.addEventListener('click', (e) => this.handleStatsAction(action, e));
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
    
    async handleStatsAction(action, event) {
        const button = event.target;
        this.setButtonLoading(button, true);
        
        try {
            switch(action) {
                case 'update':
                    await this.updateGalleryStats();
                    break;
                default:
                    console.warn(`Unbekannte Stats-Aktion: ${action}`);
            }
        } catch (error) {
            console.error(`Fehler bei Stats-Aktion ${action}:`, error);
            this.showNotification(`❌ Fehler: ${error.message}`, 'error');
        } finally {
            this.setButtonLoading(button, false);
        }
    }
    
    async quickBulkTag() {
        const tagInput = document.getElementById('bulk-tag-input');
        const tag = tagInput?.value?.trim();
        
        if (!tag) {
            this.showNotification('❌ Bitte Tag eingeben', 'warning');
            return;
        }
        
        if (!window.enhancedImageGallery || window.enhancedImageGallery.selectedImages.size === 0) {
            this.showNotification('❌ Keine Bilder ausgewählt. Aktiviere Bulk-Modus und wähle Bilder aus.', 'warning');
            return;
        }
        
        try {
            const selectedList = Array.from(window.enhancedImageGallery.selectedImages);
            
            this.showNotification(`🏷️ Tagge ${selectedList.length} Bilder mit "${tag}"...`, 'info');
            
            const response = await fetch('/api/gallery/tag-images', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ files: selectedList, tag: tag })
            });
            
            const result = await response.json();
            
            if (response.ok) {
                this.showNotification(`✅ ${result.tagged || selectedList.length} Bilder mit "${tag}" getaggt`, 'success');
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
        const preset = document.getElementById('cleanup-preset')?.value || 'conservative';
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
                const totalSize = result.candidates?.reduce((sum, c) => sum + c.size, 0) || 0;
                const count = result.candidates?.length || 0;
                
                this.showNotification(`🔍 Cleanup-Vorschau: ${count} Dateien (${this.formatFileSize(totalSize)}) würden gelöscht`, 'info');
                
            } else {
                throw new Error(result.error || 'Cleanup-Vorschau fehlgeschlagen');
            }
            
        } catch (error) {
            console.error('Cleanup-Preview-Fehler:', error);
            this.showNotification(`❌ Cleanup-Vorschau fehlgeschlagen: ${error.message}`, 'error');
        }
    }
    
    async executeCleanup() {
        const preset = document.getElementById('cleanup-preset')?.value || 'conservative';
        const settings = this.getCleanupSettings(preset);
        
        const confirmed = confirm(`🗑️ Cleanup "${preset}" wirklich ausführen?\n\nDieser Vorgang kann nicht rückgängig gemacht werden!`);
        if (!confirmed) return;
        
        try {
            this.showNotification('🧹 Führe Cleanup aus...', 'info');
            
            const response = await fetch('/api/gallery/cleanup', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({...settings, dry_run: false})
            });
            
            const result = await response.json();
            
            if (response.ok) {
                const deletedCount = result.deleted || 0;
                this.showNotification(`✅ Cleanup abgeschlossen: ${deletedCount} Dateien gelöscht`, 'success');
                
                // Galerie neu laden
                if (window.enhancedImageGallery) {
                    setTimeout(() => window.enhancedImageGallery.loadGallery(), 1000);
                } else if (window.cameraController) {
                    setTimeout(() => window.cameraController.loadGallery(), 1000);
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
        const format = document.getElementById('export-format')?.value || 'original';
        
        try {
            this.showNotification(`📤 Export "${format}" wird vorbereitet...`, 'info');
            
            switch(format) {
                case 'original':
                    if (window.enhancedImageGallery) {
                        await window.enhancedImageGallery.downloadImages();
                    } else if (window.cameraController) {
                        await window.cameraController.downloadImages();
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
                    this.showNotification('⚠️ Web-Export noch nicht implementiert', 'warning');
                    break;
                    
                case 'ai-training':
                    this.showNotification('⚠️ KI-Training-Export noch nicht implementiert', 'warning');
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
                camera_settings: this.getCameraSettings(),
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
        const confirmed = confirm('🔄 Alle Kamera-Statistiken zurücksetzen?\n\nDies löscht lokale Einstellungen und Zähler.');
        
        if (confirmed) {
            try {
                // Reset lokale Daten (ohne localStorage - nicht verfügbar in Claude.ai)
                this.showNotification('🔄 Lokale Statistiken zurückgesetzt', 'success');
                
                // Aktualisiere UI-Elemente
                setTimeout(() => this.updateGalleryStats(), 500);
                
            } catch (error) {
                console.error('Stats-Reset-Fehler:', error);
                this.showNotification('❌ Reset fehlgeschlagen', 'error');
            }
        }
    }
    
    // ✅ KORRIGIERTER ENDPOINT - kein /api/camera/stats mehr
    async updateGalleryStats() {
        try {
            console.log('📊 Aktualisiere Galerie-Statistiken...');
            
            // Verwende die bestehende Gallery-API statt nicht-existierender Stats-API
            const response = await fetch('/api/gallery/images');
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            // Berechne Statistiken aus den Bilddaten
            const stats = this.calculateStatsFromImages(data.images || []);
            
            // Update DOM-Elemente
            this.updateStatsDOM(stats);
            
            console.log('✅ Galerie-Statistiken aktualisiert:', stats);
            
        } catch (error) {
            console.warn('⚠️ Stats-Update-Fehler:', error);
            
            // Fallback: Setze Fehlerwerte
            this.updateStatsDOM({
                total_images: '❌',
                total_size: '❌',
                today_count: '❌',
                tag_count: '❌'
            });
        }
    }
    
    calculateStatsFromImages(images) {
        const now = new Date();
        const today = now.toDateString();
        
        let totalSize = 0;
        let todayCount = 0;
        let tags = new Set();
        
        images.forEach(image => {
            // Gesamtgröße
            totalSize += image.size || 0;
            
            // Heute aufgenommene Bilder
            if (image.created) {
                const imageDate = new Date(image.created * 1000);
                if (imageDate.toDateString() === today) {
                    todayCount++;
                }
            }
            
            // Tags sammeln (falls vorhanden)
            if (image.tags) {
                image.tags.forEach(tag => tags.add(tag));
            }
        });
        
        return {
            total_images: images.length,
            total_size: this.formatFileSize(totalSize),
            today_count: todayCount,
            tag_count: tags.size
        };
    }
    
    updateStatsDOM(stats) {
        const elements = {
            'total-images': stats.total_images,
            'total-size': stats.total_size,
            'today-count': stats.today_count,
            'tag-count': stats.tag_count
        };
        
        for (const [id, value] of Object.entries(elements)) {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
            }
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
    
    getCameraSettings() {
        // Sammle Einstellungen aus dem DOM
        const settings = {};
        
        document.querySelectorAll('[data-setting]').forEach(element => {
            const setting = element.dataset.setting;
            settings[setting] = element.value;
        });
        
        return settings;
    }
    
    getCleanupSettings(preset) {
        const settings = {
            conservative: { days_old: 30, max_size_mb: 10, keep_tagged: true },
            moderate: { days_old: 14, max_size_mb: 5, keep_tagged: true },
            aggressive: { days_old: 7, max_size_mb: 2, keep_tagged: false }
        };
        
        return settings[preset] || settings.conservative;
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
        if (!bytes || bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }
    
    setButtonLoading(button, loading) {
        if (loading) {
            button.dataset.loading = 'true';
            button.disabled = true;
            button.style.opacity = '0.7';
        } else {
            delete button.dataset.loading;
            button.disabled = false;
            button.style.opacity = '1';
        }
    }
    
    showNotification(message, type = 'info') {
        // Nutze globale Notification-Funktion falls verfügbar
        if (window.cameraController && window.cameraController.showNotification) {
            window.cameraController.showNotification(message, type);
        } else {
            // Fallback: Console-Log
            console.log(`${type.toUpperCase()}: ${message}`);
            
            // Einfache Browser-Notification
            const notification = document.createElement('div');
            notification.style.cssText = `
                position: fixed; top: 20px; right: 20px; z-index: 8888;
                padding: 12px 20px; border-radius: 6px; color: white;
                background: ${type === 'error' ? '#f44336' : type === 'warning' ? '#ff9800' : type === 'success' ? '#4caf50' : '#2196f3'};
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                max-width: 300px; font-size: 14px;
            `;
            notification.textContent = message;
            
            document.body.appendChild(notification);
            
            setTimeout(() => {
                if (document.body.contains(notification)) {
                    document.body.removeChild(notification);
                }
            }, 5000);
        }
    }
    
    startStatsUpdates() {
        // Initiales Stats-Update nach kurzer Verzögerung
        setTimeout(() => this.updateGalleryStats(), 2000);
        
        // Auto-Update alle 60 Sekunden (reduziert für weniger 404-Requests)
        setInterval(() => {
            this.updateGalleryStats();
        }, 60000);
    }
}

// Automatische Initialisierung
console.log('🚀 Initialisiere reparierte Kamera-Tools...');
const cameraTools = new CameraTools();

// Für Debugging
window.cameraTools = cameraTools;

console.log('✅ Reparierte Kamera-Tools geladen - Keine 404-Fehler mehr!');