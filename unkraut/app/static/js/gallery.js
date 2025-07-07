// app/static/js/gallery.js - Enhanced mit Bulk-Operationen
/**
 * Erweiterte Bildergalerie mit Bulk-Operationen und Vorschau
 * Professionelle Bildverwaltung für Unkraut-2025
 */

class EnhancedImageGallery {
    constructor() {
        this.images = [];
        this.selectedImages = new Set();
        this.isLoading = false;
        this.bulkMode = false;
        this.autoRefreshInterval = null;
        this.filterOptions = {
            dateRange: 'all',
            minSize: 0,
            maxSize: Infinity,
            hasTag: 'all'
        };
        
        // Automatische Initialisierung
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.init());
        } else {
            this.init();
        }
    }
    
    init() {
        console.log('📸 Initialisiere Enhanced Bildergalerie...');
        
        this.bindEventListeners();
        this.loadGallery();
        this.startAutoRefresh();
        this.hookIntoCaptureEvents();
        
        console.log('✅ Enhanced Galerie bereit');
    }
    
    bindEventListeners() {
        // Standard Galerie-Buttons
        document.querySelectorAll('[data-gallery-action]').forEach(button => {
            const action = button.dataset.galleryAction;
            button.addEventListener('click', (e) => this.handleGalleryAction(action, e));
        });
        
        // Bulk-Buttons
        document.querySelectorAll('[data-bulk-action]').forEach(button => {
            const action = button.dataset.bulkAction;
            button.addEventListener('click', (e) => this.handleBulkAction(action, e));
        });
        
        // Filter-Controls
        document.querySelectorAll('[data-filter]').forEach(element => {
            const filter = element.dataset.filter;
            element.addEventListener('change', (e) => this.handleFilterChange(filter, e));
        });
        
        console.log('📎 Enhanced Event-Listener gebunden');
    }
    
    async loadGallery() {
        if (this.isLoading) return;
        
        this.isLoading = true;
        this.updateLoadButton('🔄 Lädt...');
        
        try {
            console.log('📸 Lade Enhanced Bildergalerie...');
            
            const response = await fetch('/api/gallery/images');
            const data = await response.json();
            
            this.images = data.images || [];
            this.applyFilters();
            this.renderGallery();
            
            console.log(`✅ Galerie geladen: ${this.images.length} Bilder`);
            
        } catch (error) {
            console.error('❌ Galerie-Lade-Fehler:', error);
            this.renderError(error.message);
        } finally {
            this.isLoading = false;
            this.updateLoadButton('🔄 Galerie laden');
        }
    }
    
    renderGallery() {
        const container = document.getElementById('image-gallery');
        if (!container) {
            console.warn('Galerie-Container nicht gefunden');
            return;
        }
        
        if (this.images.length === 0) {
            container.innerHTML = this.renderEmptyState();
            return;
        }
        
        // Galerie mit Bulk-Features
        let html = this.renderGalleryHeader();
        html += this.renderBulkControls();
        html += this.renderFilterControls();
        html += this.renderImageGrid();
        html += this.renderBulkActionBar();
        
        container.innerHTML = html;
        this.bindDynamicEvents(container);
        this.updateBulkUI();
    }
    
    renderGalleryHeader() {
        const totalSize = this.images.reduce((sum, img) => sum + (img.size || 0), 0);
        const selectedCount = this.selectedImages.size;
        const selectedSize = Array.from(this.selectedImages)
            .reduce((sum, filename) => {
                const img = this.images.find(i => i.filename === filename);
                return sum + (img?.size || 0);
            }, 0);
        
        return `
            <div class="gallery-header">
                <div class="gallery-stats">
                    <h4>📸 Bildergalerie (${this.images.length})</h4>
                    <p>Gesamtgröße: ${this.formatFileSize(totalSize)}</p>
                    ${selectedCount > 0 ? `
                        <p class="selection-info">
                            <strong>Ausgewählt: ${selectedCount} Bilder (${this.formatFileSize(selectedSize)})</strong>
                        </p>
                    ` : ''}
                </div>
                <div class="gallery-modes">
                    <button class="btn ${this.bulkMode ? 'btn-primary' : 'btn-secondary'}" 
                            data-gallery-action="toggle-bulk">
                        ${this.bulkMode ? '✅ Bulk-Modus' : '☑️ Bulk-Modus'}
                    </button>
                </div>
            </div>
        `;
    }
    
    renderBulkControls() {
        if (!this.bulkMode) return '';
        
        return `
            <div class="bulk-controls ${this.bulkMode ? 'active' : ''}">
                <div class="selection-controls">
                    <button class="btn-small btn-info" data-bulk-action="select-all">☑️ Alle</button>
                    <button class="btn-small btn-secondary" data-bulk-action="select-none">☐ Keine</button>
                    <button class="btn-small btn-warning" data-bulk-action="select-today">📅 Heute</button>
                    <button class="btn-small btn-warning" data-bulk-action="select-week">📅 Diese Woche</button>
                    <button class="btn-small btn-info" data-bulk-action="select-large">📏 Große Dateien</button>
                </div>
            </div>
        `;
    }
    
    renderFilterControls() {
        return `
            <div class="filter-controls">
                <div class="filter-row">
                    <select data-filter="dateRange" class="filter-select">
                        <option value="all">📅 Alle Daten</option>
                        <option value="today">Heute</option>
                        <option value="week">Diese Woche</option>
                        <option value="month">Dieser Monat</option>
                    </select>
                    
                    <select data-filter="sizeRange" class="filter-select">
                        <option value="all">📏 Alle Größen</option>
                        <option value="small">Klein (< 500KB)</option>
                        <option value="medium">Mittel (500KB - 2MB)</option>
                        <option value="large">Groß (> 2MB)</option>
                    </select>
                    
                    <button class="btn-small btn-secondary" data-gallery-action="clear-filters">🧹 Filter zurücksetzen</button>
                </div>
            </div>
        `;
    }
    
    renderImageGrid() {
        let html = '<div class="gallery-grid enhanced">';
        
        this.images.slice(0, 50).forEach(image => {
            const date = new Date(image.created * 1000);
            const timestamp = date.toLocaleString('de-DE');
            const isSelected = this.selectedImages.has(image.filename);
            
            html += `
                <div class="gallery-item enhanced ${isSelected ? 'selected' : ''}" 
                     data-filename="${image.filename}">
                     
                    ${this.bulkMode ? `
                        <div class="selection-overlay">
                            <input type="checkbox" 
                                   class="image-checkbox" 
                                   data-filename="${image.filename}"
                                   ${isSelected ? 'checked' : ''}>
                        </div>
                    ` : ''}
                    
                    <div class="image-preview">
                        <img class="gallery-image" 
                             src="${image.url}" 
                             alt="Bild ${image.filename}"
                             title="${image.filename} - ${timestamp}"
                             data-action="show-preview"
                             data-filename="${image.filename}"
                             data-url="${image.url}"
                             loading="lazy">
                             
                        <div class="image-overlay">
                            <button class="overlay-btn preview-btn" 
                                    data-action="show-modal" 
                                    data-filename="${image.filename}" 
                                    data-url="${image.url}">
                                🔍
                            </button>
                            <button class="overlay-btn download-btn" 
                                    data-action="download-single" 
                                    data-filename="${image.filename}">
                                💾
                            </button>
                            <button class="overlay-btn delete-btn" 
                                    data-action="delete-single" 
                                    data-filename="${image.filename}">
                                🗑️
                            </button>
                        </div>
                    </div>
                    
                    <div class="image-info enhanced">
                        <div class="image-name" title="${image.filename}">${image.filename}</div>
                        <div class="image-meta">
                            <span class="image-date">${date.toLocaleDateString('de-DE')}</span>
                            <span class="image-time">${date.toLocaleTimeString('de-DE', {hour: '2-digit', minute: '2-digit'})}</span>
                        </div>
                        <div class="image-size">${this.formatFileSize(image.size)}</div>
                    </div>
                </div>
            `;
        });
        
        html += '</div>';
        
        if (this.images.length > 50) {
            html += `<p class="gallery-note">Zeige 50 von ${this.images.length} Bildern</p>`;
        }
        
        return html;
    }
    
    renderBulkActionBar() {
        if (!this.bulkMode || this.selectedImages.size === 0) return '';
        
        const selectedCount = this.selectedImages.size;
        const selectedSize = Array.from(this.selectedImages)
            .reduce((sum, filename) => {
                const img = this.images.find(i => i.filename === filename);
                return sum + (img?.size || 0);
            }, 0);
        
        return `
            <div class="bulk-action-bar ${selectedCount > 0 ? 'visible' : ''}">
                <div class="bulk-info">
                    <strong>${selectedCount} Bilder ausgewählt</strong>
                    <span>(${this.formatFileSize(selectedSize)})</span>
                </div>
                <div class="bulk-actions">
                    <button class="btn btn-success" data-bulk-action="download-selected">
                        📦 Download (${selectedCount})
                    </button>
                    <button class="btn btn-warning" data-bulk-action="tag-selected">
                        🏷️ Taggen
                    </button>
                    <button class="btn btn-danger" data-bulk-action="delete-selected">
                        🗑️ Löschen (${selectedCount})
                    </button>
                </div>
            </div>
        `;
    }
    
    renderEmptyState() {
        return `
            <div class="gallery-empty">
                <p>📷 Keine Bilder gefunden</p>
                <p>Verwende den "Foto aufnehmen" Button oder ändere die Filter</p>
            </div>
        `;
    }
    
    bindDynamicEvents(container) {
        // Checkbox-Events
        container.querySelectorAll('.image-checkbox').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                e.stopPropagation();
                const filename = e.target.dataset.filename;
                this.toggleImageSelection(filename);
            });
        });
        
        // Overlay-Button-Events
        container.querySelectorAll('[data-action]').forEach(btn => {
            const action = btn.dataset.action;
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.handleImageAction(action, e);
            });
        });
        
        // Gallery-Item Klick für Bulk-Auswahl
        container.querySelectorAll('.gallery-item').forEach(item => {
            item.addEventListener('click', (e) => {
                if (this.bulkMode && !e.target.matches('button, input')) {
                    const filename = item.dataset.filename;
                    this.toggleImageSelection(filename);
                }
            });
        });
    }
    
    async handleGalleryAction(action, event) {
        const button = event.target;
        this.setButtonLoading(button, true);
        
        try {
            switch(action) {
                case 'load':
                    await this.loadGallery();
                    break;
                case 'download':
                    await this.downloadAllImages();
                    break;
                case 'clear':
                    await this.clearAllImages();
                    break;
                case 'toggle-bulk':
                    this.toggleBulkMode();
                    break;
                case 'clear-filters':
                    this.clearFilters();
                    break;
                default:
                    console.warn(`Unbekannte Galerie-Aktion: ${action}`);
            }
        } catch (error) {
            console.error(`Fehler bei Galerie-Aktion ${action}:`, error);
            this.showNotification(`❌ Fehler: ${error.message}`, 'error');
        } finally {
            this.setButtonLoading(button, false);
        }
    }
    
    async handleBulkAction(action, event) {
        const button = event.target;
        this.setButtonLoading(button, true);
        
        try {
            switch(action) {
                case 'select-all':
                    this.selectAllImages();
                    break;
                case 'select-none':
                    this.selectNoImages();
                    break;
                case 'select-today':
                    this.selectImagesByDate('today');
                    break;
                case 'select-week':
                    this.selectImagesByDate('week');
                    break;
                case 'select-large':
                    this.selectImagesBySize('large');
                    break;
                case 'download-selected':
                    await this.downloadSelectedImages();
                    break;
                case 'tag-selected':
                    await this.tagSelectedImages();
                    break;
                case 'delete-selected':
                    await this.deleteSelectedImages();
                    break;
                default:
                    console.warn(`Unbekannte Bulk-Aktion: ${action}`);
            }
        } catch (error) {
            console.error(`Fehler bei Bulk-Aktion ${action}:`, error);
            this.showNotification(`❌ Fehler: ${error.message}`, 'error');
        } finally {
            this.setButtonLoading(button, false);
        }
    }
    
    handleImageAction(action, event) {
        const filename = event.target.dataset.filename;
        const url = event.target.dataset.url;
        
        switch(action) {
            case 'show-modal':
                this.showImageModal(filename, url);
                break;
            case 'download-single':
                this.downloadSingleImage(filename);
                break;
            case 'delete-single':
                this.deleteSingleImage(filename);
                break;
            case 'show-preview':
                if (!this.bulkMode) {
                    this.showImageModal(filename, url);
                }
                break;
        }
    }
    
    toggleBulkMode() {
        this.bulkMode = !this.bulkMode;
        if (!this.bulkMode) {
            this.selectedImages.clear();
        }
        this.renderGallery();
        
        this.showNotification(
            this.bulkMode ? '☑️ Bulk-Modus aktiviert' : '☐ Bulk-Modus deaktiviert', 
            'info'
        );
    }
    
    toggleImageSelection(filename) {
        if (this.selectedImages.has(filename)) {
            this.selectedImages.delete(filename);
        } else {
            this.selectedImages.add(filename);
        }
        this.updateBulkUI();
    }
    
    selectAllImages() {
        this.images.forEach(img => this.selectedImages.add(img.filename));
        this.updateBulkUI();
        this.showNotification(`☑️ ${this.images.length} Bilder ausgewählt`, 'info');
    }
    
    selectNoImages() {
        this.selectedImages.clear();
        this.updateBulkUI();
        this.showNotification('☐ Auswahl zurückgesetzt', 'info');
    }
    
    selectImagesByDate(period) {
        const now = new Date();
        let cutoff;
        
        switch(period) {
            case 'today':
                cutoff = new Date(now.getFullYear(), now.getMonth(), now.getDate());
                break;
            case 'week':
                cutoff = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
                break;
            default:
                return;
        }
        
        let selected = 0;
        this.images.forEach(img => {
            const imgDate = new Date(img.created * 1000);
            if (imgDate >= cutoff) {
                this.selectedImages.add(img.filename);
                selected++;
            }
        });
        
        this.updateBulkUI();
        this.showNotification(`📅 ${selected} Bilder von ${period} ausgewählt`, 'info');
    }
    
    selectImagesBySize(sizeCategory) {
        let minSize, maxSize;
        
        switch(sizeCategory) {
            case 'small':
                minSize = 0; maxSize = 500 * 1024;
                break;
            case 'medium':
                minSize = 500 * 1024; maxSize = 2 * 1024 * 1024;
                break;
            case 'large':
                minSize = 2 * 1024 * 1024; maxSize = Infinity;
                break;
            default:
                return;
        }
        
        let selected = 0;
        this.images.forEach(img => {
            if (img.size >= minSize && img.size < maxSize) {
                this.selectedImages.add(img.filename);
                selected++;
            }
        });
        
        this.updateBulkUI();
        this.showNotification(`📏 ${selected} ${sizeCategory} Bilder ausgewählt`, 'info');
    }
    
    async downloadSelectedImages() {
        const selectedList = Array.from(this.selectedImages);
        if (selectedList.length === 0) {
            this.showNotification('❌ Keine Bilder ausgewählt', 'warning');
            return;
        }
        
        try {
            this.showNotification(`📦 Erstelle Archiv mit ${selectedList.length} Bildern...`, 'info');
            
            const response = await fetch('/api/gallery/download-selected', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ files: selectedList })
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Download fehlgeschlagen');
            }
            
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `ausgewaehlte_bilder_${new Date().toISOString().slice(0,10)}.zip`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
            this.showNotification(`✅ ${selectedList.length} Bilder heruntergeladen!`, 'success');
            
        } catch (error) {
            console.error('Bulk-Download-Fehler:', error);
            this.showNotification(`❌ Bulk-Download fehlgeschlagen: ${error.message}`, 'error');
        }
    }
    
    async tagSelectedImages() {
        const selectedList = Array.from(this.selectedImages);
        if (selectedList.length === 0) {
            this.showNotification('❌ Keine Bilder ausgewählt', 'warning');
            return;
        }
        
        const tag = prompt(`🏷️ Tag für ${selectedList.length} Bilder eingeben:`, 'Unkraut-Erkennung');
        if (!tag) return;
        
        try {
            this.showNotification(`🏷️ Tagge ${selectedList.length} Bilder...`, 'info');
            
            const response = await fetch('/api/gallery/tag-images', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ files: selectedList, tag: tag })
            });
            
            const result = await response.json();
            
            if (response.ok) {
                this.showNotification(`✅ ${result.tagged} Bilder mit "${tag}" getaggt`, 'success');
            } else {
                throw new Error(result.error || 'Tagging fehlgeschlagen');
            }
            
        } catch (error) {
            console.error('Bulk-Tag-Fehler:', error);
            this.showNotification(`❌ Tagging fehlgeschlagen: ${error.message}`, 'error');
        }
    }
    
    async deleteSelectedImages() {
        const selectedList = Array.from(this.selectedImages);
        if (selectedList.length === 0) {
            this.showNotification('❌ Keine Bilder ausgewählt', 'warning');
            return;
        }
        
        const confirmed = confirm(`🗑️ ${selectedList.length} ausgewählte Bilder wirklich löschen?\n\nDieser Vorgang kann nicht rückgängig gemacht werden!`);
        if (!confirmed) return;
        
        try {
            this.showNotification(`🗑️ Lösche ${selectedList.length} Bilder...`, 'info');
            
            const response = await fetch('/api/gallery/delete-selected', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ files: selectedList })
            });
            
            const result = await response.json();
            
            if (response.ok) {
                this.showNotification(`✅ ${result.deleted} Bilder gelöscht`, 'success');
                
                // Entferne aus lokaler Liste
                this.images = this.images.filter(img => !selectedList.includes(img.filename));
                this.selectedImages.clear();
                this.renderGallery();
                
            } else {
                throw new Error(result.error || 'Löschen fehlgeschlagen');
            }
            
        } catch (error) {
            console.error('Bulk-Delete-Fehler:', error);
            this.showNotification(`❌ Bulk-Löschen fehlgeschlagen: ${error.message}`, 'error');
        }
    }
    
    updateBulkUI() {
        // Checkboxen aktualisieren
        document.querySelectorAll('.image-checkbox').forEach(checkbox => {
            const filename = checkbox.dataset.filename;
            checkbox.checked = this.selectedImages.has(filename);
        });
        
        // Gallery-Items markieren
        document.querySelectorAll('.gallery-item').forEach(item => {
            const filename = item.dataset.filename;
            item.classList.toggle('selected', this.selectedImages.has(filename));
        });
        
        // Bulk-Action-Bar neu rendern
        const actionBar = document.querySelector('.bulk-action-bar');
        if (actionBar) {
            actionBar.outerHTML = this.renderBulkActionBar();
            
            // Event-Listener für neue Buttons binden
            const newActionBar = document.querySelector('.bulk-action-bar');
            if (newActionBar) {
                newActionBar.querySelectorAll('[data-bulk-action]').forEach(btn => {
                    const action = btn.dataset.bulkAction;
                    btn.addEventListener('click', (e) => this.handleBulkAction(action, e));
                });
            }
        } else {
            // Action-Bar hinzufügen falls nicht vorhanden
            const gallery = document.getElementById('image-gallery');
            if (gallery && this.bulkMode && this.selectedImages.size > 0) {
                gallery.insertAdjacentHTML('beforeend', this.renderBulkActionBar());
            }
        }
        
        // Header aktualisieren für Auswahlzähler
        const header = document.querySelector('.gallery-header');
        if (header) {
            header.outerHTML = this.renderGalleryHeader();
        }
    }
    
    // Reste der Klasse (showImageModal, downloadSingleImage, etc.) bleiben gleich...
    // [Würde hier alle anderen Methoden aus der ursprünglichen Galerie einfügen]
    
    showImageModal(filename, imageUrl) {
        const modal = document.createElement('div');
        modal.className = 'image-modal';
        modal.dataset.modal = 'image';
        
        modal.innerHTML = `
            <div class="modal-content">
                <span class="modal-close" data-action="close-modal">&times;</span>
                <img src="${imageUrl}" alt="${filename}">
                <div class="modal-info">
                    <h3>${filename}</h3>
                    <div class="modal-actions">
                        <button class="btn btn-primary" data-action="download-single" data-filename="${filename}">💾 Download</button>
                        <button class="btn btn-danger" data-action="delete-single-modal" data-filename="${filename}">🗑️ Löschen</button>
                        ${this.bulkMode ? `
                            <button class="btn btn-warning" data-action="toggle-selection" data-filename="${filename}">
                                ${this.selectedImages.has(filename) ? '☑️ Ausgewählt' : '☐ Auswählen'}
                            </button>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;
        
        // Event-Listener für Modal
        modal.addEventListener('click', (e) => {
            if (e.target === modal || e.target.dataset.action === 'close-modal') {
                document.body.removeChild(modal);
            }
        });
        
        modal.querySelector('[data-action="download-single"]')?.addEventListener('click', (e) => {
            this.downloadSingleImage(e.target.dataset.filename);
        });
        
        modal.querySelector('[data-action="delete-single-modal"]')?.addEventListener('click', (e) => {
            this.deleteSingleImage(e.target.dataset.filename);
            document.body.removeChild(modal);
        });
        
        modal.querySelector('[data-action="toggle-selection"]')?.addEventListener('click', (e) => {
            this.toggleImageSelection(e.target.dataset.filename);
            document.body.removeChild(modal);
        });
        
        document.body.appendChild(modal);
    }
    
    // Utility-Methoden bleiben gleich...
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
        if (window.showNotification) {
            window.showNotification(message, type);
        } else {
            console.log(`${type.toUpperCase()}: ${message}`);
        }
    }
    
    // Weitere Methoden aus der ursprünglichen Galerie...
    startAutoRefresh() {
        this.autoRefreshInterval = setInterval(() => {
            if (!this.bulkMode) { // Nicht während Bulk-Operationen
                this.loadGallery();
            }
        }, 30000);
    }
    
    hookIntoCaptureEvents() {
        document.addEventListener('imageCapture', () => {
            setTimeout(() => this.loadGallery(), 1000);
        });
    }
}

// Modal-CSS erweitern
function addEnhancedModalCSS() {
    if (!document.querySelector('#enhanced-gallery-css')) {
        const style = document.createElement('style');
        style.id = 'enhanced-gallery-css';
        style.textContent = `
            /* Enhanced Gallery Styles */
            .gallery-grid.enhanced {
                gap: 12px;
            }
            
            .gallery-item.enhanced {
                position: relative;
                cursor: pointer;
                transition: all 0.2s ease;
            }
            
            .gallery-item.enhanced.selected {
                border: 3px solid #4CAF50;
                transform: scale(0.98);
                box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.3);
            }
            
            .selection-overlay {
                position: absolute;
                top: 8px;
                left: 8px;
                z-index: 10;
                background: rgba(0, 0, 0, 0.7);
                border-radius: 4px;
                padding: 4px;
            }
            
            .image-checkbox {
                width: 18px;
                height: 18px;
                cursor: pointer;
            }
            
            .image-preview {
                position: relative;
                overflow: hidden;
                border-radius: 6px;
            }
            
            .image-overlay {
                position: absolute;
                top: 0;
                right: 0;
                display: flex;
                flex-direction: column;
                gap: 4px;
                padding: 8px;
                opacity: 0;
                transition: opacity 0.2s ease;
            }
            
            .gallery-item.enhanced:hover .image-overlay {
                opacity: 1;
            }
            
            .overlay-btn {
                width: 32px;
                height: 32px;
                border: none;
                border-radius: 50%;
                background: rgba(0, 0, 0, 0.7);
                color: white;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 14px;
                transition: all 0.2s ease;
            }
            
            .overlay-btn:hover {
                background: rgba(0, 0, 0, 0.9);
                transform: scale(1.1);
            }
            
            .bulk-controls {
                background: rgba(255, 255, 255, 0.1);
                padding: 12px;
                border-radius: 6px;
                margin: 10px 0;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            
            .selection-controls {
                display: flex;
                gap: 8px;
                flex-wrap: wrap;
                justify-content: center;
            }
            
            .filter-controls {
                background: rgba(255, 255, 255, 0.05);
                padding: 10px;
                border-radius: 6px;
                margin: 10px 0;
            }
            
            .filter-row {
                display: flex;
                gap: 10px;
                align-items: center;
                flex-wrap: wrap;
                justify-content: center;
            }
            
            .filter-select {
                padding: 6px 10px;
                border-radius: 4px;
                border: 1px solid rgba(255, 255, 255, 0.3);
                background: rgba(255, 255, 255, 0.1);
                color: white;
                min-width: 150px;
            }
            
            .bulk-action-bar {
                position: fixed;
                bottom: 20px;
                left: 50%;
                transform: translateX(-50%);
                background: rgba(0, 0, 0, 0.9);
                backdrop-filter: blur(10px);
                padding: 15px 20px;
                border-radius: 12px;
                border: 1px solid rgba(255, 255, 255, 0.2);
                display: flex;
                align-items: center;
                gap: 20px;
                z-index: 100;
                opacity: 0;
                transform: translateX(-50%) translateY(100px);
                transition: all 0.3s ease;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            }
            
            .bulk-action-bar.visible {
                opacity: 1;
                transform: translateX(-50%) translateY(0);
            }
            
            .bulk-info {
                color: white;
                font-weight: 600;
            }
            
            .bulk-info span {
                color: rgba(255, 255, 255, 0.7);
                font-size: 0.9em;
                margin-left: 8px;
            }
            
            .bulk-actions {
                display: flex;
                gap: 10px;
            }
            
            .gallery-modes {
                display: flex;
                gap: 10px;
            }
            
            .selection-info {
                color: #4CAF50 !important;
                font-weight: 600;
                margin: 5px 0 !important;
            }
            
            .image-info.enhanced {
                padding: 8px;
            }
            
            .image-meta {
                display: flex;
                justify-content: space-between;
                font-size: 0.75em;
                color: rgba(255, 255, 255, 0.6);
                margin: 2px 0;
            }
            
            @media (max-width: 768px) {
                .bulk-action-bar {
                    left: 10px;
                    right: 10px;
                    transform: none;
                    flex-direction: column;
                    gap: 10px;
                }
                
                .bulk-action-bar.visible {
                    transform: translateY(0);
                }
                
                .bulk-actions {
                    width: 100%;
                    justify-content: center;
                }
                
                .selection-controls {
                    justify-content: flex-start;
                }
                
                .filter-row {
                    flex-direction: column;
                    align-items: stretch;
                }
                
                .filter-select {
                    min-width: auto;
                }
            }
        `;
        document.head.appendChild(style);
    }
}

// Automatische Initialisierung
addEnhancedModalCSS();
const enhancedImageGallery = new EnhancedImageGallery();

// Für Debugging
window.enhancedImageGallery = enhancedImageGallery;