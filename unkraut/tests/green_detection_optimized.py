# unkraut/ai/weed_detection_optimized.py
"""
Optimierte Grün-Erkennung für Unkraut-2025
Erweiterte OpenCV-Algorithmen + Mock-Funktionen
"""
import cv2
import numpy as np
import time
import random
from datetime import datetime
import logging

class WeedDetector:
    def __init__(self):
        self.model_loaded = False
        self.model = None
        self.detection_count = 0
        self.debug_mode = True
        
        # Erweiterte Einstellungen
        self.settings = {
            'confidence_threshold': 0.5,
            'min_area': 300,           # Minimale Objektgröße (Pixel²)
            'max_area': 10000,         # Maximale Objektgröße
            'sensitivity': 0.7,        # Erkennungsempfindlichkeit (0.1-1.0)
            'blur_kernel': 5,          # Blur-Größe
            'morph_kernel': 5,         # Morphology-Kernel
            'contour_approximation': 2  # Kontur-Vereinfachung
        }
        
        # Verschiedene Grün-Profile
        self.green_profiles = {
            'bright': {
                'lower': np.array([35, 50, 50]),
                'upper': np.array([85, 255, 255]),
                'name': 'Helles Grün'
            },
            'dark': {
                'lower': np.array([30, 30, 30]),
                'upper': np.array([90, 255, 200]),
                'name': 'Dunkles Grün'
            },
            'mixed': {
                'lower': np.array([25, 40, 40]),
                'upper': np.array([95, 255, 255]),
                'name': 'Gemischtes Grün'
            }
        }
        
        self.current_profile = 'mixed'
        self.init_detector()
    
    def init_detector(self):
        """Detektor initialisieren"""
        try:
            # Versuche TensorFlow zu laden (für später)
            import tensorflow as tf
            self.log("⚠️ TensorFlow verfügbar, aber kein Modell geladen")
            self.log("💡 Verwende optimierte OpenCV-Erkennung")
            
        except ImportError:
            self.log("⚠️ TensorFlow nicht installiert - nur OpenCV")
            
        self.model_loaded = False
        self.log("🔧 Optimierte Grün-Erkennung aktiviert")
    
    def log(self, message):
        """Debug-Logging"""
        if self.debug_mode:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] WeedDetector: {message}")
    
    def detect_from_bytes(self, image_bytes):
        """Unkraut in Bild-Bytes erkennen"""
        try:
            # Bytes zu OpenCV-Bild konvertieren
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                return {'error': 'Invalid image data'}
            
            return self.detect_in_image(image)
            
        except Exception as e:
            return {'error': f'Detection failed: {str(e)}'}
    
    def detect_in_image(self, image):
        """Haupterkennungsfunktion"""
        start_time = time.time()
        
        try:
            # Verschiedene Erkennungsmodi
            if self.model_loaded and self.model:
                detections = self._tensorflow_detection(image)
            else:
                detections = self._enhanced_opencv_detection(image)
            
            processing_time = time.time() - start_time
            self.detection_count += 1
            
            # Vollständiges Ergebnis
            result = {
                'detections': detections,
                'count': len(detections),
                'confidence': self._calculate_average_confidence(detections),
                'processing_time': round(processing_time, 3),
                'timestamp': int(time.time()),
                'detection_id': self.detection_count,
                'image_size': {'width': image.shape[1], 'height': image.shape[0]},
                'method': 'tensorflow' if self.model_loaded else 'opencv_enhanced',
                'settings': self.settings.copy(),
                'profile': self.green_profiles[self.current_profile]['name']
            }
            
            self.log(f"✅ Erkennung #{self.detection_count}: {len(detections)} Objekte in {processing_time:.3f}s")
            return result
            
        except Exception as e:
            self.log(f"❌ Fehler bei Erkennung: {e}")
            return {
                'error': str(e),
                'detections': [],
                'count': 0,
                'processing_time': time.time() - start_time,
                'method': 'error_fallback'
            }
    
    def _enhanced_opencv_detection(self, image):
        """Erweiterte OpenCV-Erkennung"""
        detections = []
        
        try:
            # 1. Vorverarbeitung
            processed = self._preprocess_image(image)
            
            # 2. Grün-Erkennung mit aktuellem Profil
            green_mask = self._detect_green_areas(processed)
            
            # 3. Morphologische Operationen
            cleaned_mask = self._clean_mask(green_mask)
            
            # 4. Kontur-Analyse
            contours = self._find_contours(cleaned_mask)
            
            # 5. Objektklassifizierung
            detections = self._classify_objects(contours, image)
            
            # 6. Nachbearbeitung
            detections = self._postprocess_detections(detections)
            
            return detections
            
        except Exception as e:
            self.log(f"❌ OpenCV-Erkennung fehlgeschlagen: {e}")
            return self._mock_detection(image)
    
    def _preprocess_image(self, image):
        """Bild vorverarbeiten"""
        # Gaussian Blur für Rauschreduktion
        blurred = cv2.GaussianBlur(image, (self.settings['blur_kernel'], self.settings['blur_kernel']), 0)
        
        # Zu HSV konvertieren
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
        
        return hsv
    
    def _detect_green_areas(self, hsv_image):
        """Grün-Bereiche mit aktuellem Profil erkennen"""
        profile = self.green_profiles[self.current_profile]
        
        # Basis-Maske
        mask = cv2.inRange(hsv_image, profile['lower'], profile['upper'])
        
        # Empfindlichkeit anpassen
        if self.settings['sensitivity'] < 0.5:
            # Weniger empfindlich - engere Bereiche
            mask = cv2.erode(mask, np.ones((3,3), np.uint8), iterations=1)
        elif self.settings['sensitivity'] > 0.8:
            # Sehr empfindlich - erweiterte Bereiche
            mask = cv2.dilate(mask, np.ones((3,3), np.uint8), iterations=1)
        
        return mask
    
    def _clean_mask(self, mask):
        """Maske mit morphologischen Operationen bereinigen"""
        kernel = np.ones((self.settings['morph_kernel'], self.settings['morph_kernel']), np.uint8)
        
        # Löcher schließen
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        # Kleine Objekte entfernen
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        
        return mask
    
    def _find_contours(self, mask):
        """Konturen finden und filtern"""
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Nach Größe filtern
        filtered_contours = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if self.settings['min_area'] <= area <= self.settings['max_area']:
                filtered_contours.append(contour)
        
        return filtered_contours
    
    def _classify_objects(self, contours, image):
        """Objekte klassifizieren und bewerten"""
        detections = []
        
        for i, contour in enumerate(contours):
            # Basis-Eigenschaften
            area = cv2.contourArea(contour)
            x, y, w, h = cv2.boundingRect(contour)
            center_x = x + w // 2
            center_y = y + h // 2
            
            # Erweiterte Eigenschaften
            perimeter = cv2.arcLength(contour, True)
            circularity = (4 * np.pi * area) / (perimeter ** 2) if perimeter > 0 else 0
            aspect_ratio = w / h if h > 0 else 1
            
            # Confidence-Berechnung
            confidence = self._calculate_confidence(area, circularity, aspect_ratio)
            
            # Nur wenn über Threshold
            if confidence >= self.settings['confidence_threshold']:
                detection = {
                    'class': 'weed',
                    'subclass': self._classify_weed_type(area, aspect_ratio),
                    'confidence': round(confidence, 3),
                    'bbox': {'x': x, 'y': y, 'width': w, 'height': h},
                    'center': {'x': center_x, 'y': center_y},
                    'area': int(area),
                    'circularity': round(circularity, 3),
                    'aspect_ratio': round(aspect_ratio, 3),
                    'perimeter': round(perimeter, 1),
                    'x': center_x,  # Für Roboterarm
                    'y': center_y,
                    'id': i + 1
                }
                
                detections.append(detection)
        
        return detections
    
    def _calculate_confidence(self, area, circularity, aspect_ratio):
        """Confidence-Wert berechnen"""
        # Größen-Score (optimal bei 1000-3000px²)
        optimal_size = 2000
        size_score = 1.0 - abs(area - optimal_size) / optimal_size
        size_score = max(0.1, min(1.0, size_score))
        
        # Form-Score (leicht rund bis oval)
        form_score = circularity * 0.7 + (1.0 - abs(aspect_ratio - 1.2)) * 0.3
        form_score = max(0.1, min(1.0, form_score))
        
        # Gesamt-Confidence
        confidence = (size_score * 0.6 + form_score * 0.4) * self.settings['sensitivity']
        
        return max(0.1, min(0.95, confidence))
    
    def _classify_weed_type(self, area, aspect_ratio):
        """Unkraut-Typ klassifizieren"""
        if area > 5000:
            return 'large_weed'
        elif aspect_ratio > 2.0:
            return 'grass_like'
        elif aspect_ratio < 0.5:
            return 'tall_weed'
        else:
            return 'common_weed'
    
    def _postprocess_detections(self, detections):
        """Erkennungen nachbearbeiten"""
        # Nach Confidence sortieren
        detections.sort(key=lambda x: x['confidence'], reverse=True)
        
        # Überlappende Erkennungen entfernen
        filtered_detections = []
        for detection in detections:
            if not self._is_overlapping(detection, filtered_detections):
                filtered_detections.append(detection)
        
        # Maximal 8 Erkennungen
        return filtered_detections[:8]
    
    def _is_overlapping(self, detection, existing_detections, threshold=0.3):
        """Prüfen ob Erkennung mit existierenden überlappt"""
        bbox1 = detection['bbox']
        
        for existing in existing_detections:
            bbox2 = existing['bbox']
            
            # Überlappung berechnen
            overlap = self._calculate_overlap(bbox1, bbox2)
            if overlap > threshold:
                return True
        
        return False
    
    def _calculate_overlap(self, bbox1, bbox2):
        """Überlappung zwischen zwei Bounding Boxes berechnen"""
        x1, y1, w1, h1 = bbox1['x'], bbox1['y'], bbox1['width'], bbox1['height']
        x2, y2, w2, h2 = bbox2['x'], bbox2['y'], bbox2['width'], bbox2['height']
        
        # Überlappungsbereich
        overlap_x = max(0, min(x1 + w1, x2 + w2) - max(x1, x2))
        overlap_y = max(0, min(y1 + h1, y2 + h2) - max(y1, y2))
        overlap_area = overlap_x * overlap_y
        
        # Gesamtbereich
        total_area = w1 * h1 + w2 * h2 - overlap_area
        
        return overlap_area / total_area if total_area > 0 else 0
    
    def _mock_detection(self, image):
        """Erweiterte Mock-Erkennung für Tests"""
        detections = []
        
        # Intelligentere Mock-Daten
        num_detections = random.choices([0, 1, 2, 3, 4], weights=[10, 30, 30, 20, 10])[0]
        
        h, w = image.shape[:2]
        
        for i in range(num_detections):
            # Realistische Positionen (nicht zu nah am Rand)
            x = random.randint(w//10, w - w//10 - 80)
            y = random.randint(h//10, h - h//10 - 80)
            
            # Realistische Größen
            base_size = random.randint(20, 60)
            width = base_size + random.randint(-10, 20)
            height = base_size + random.randint(-10, 20)
            
            # Realistische Confidence basierend auf Größe
            size_factor = min(1.0, base_size / 50)
            confidence = random.uniform(0.5, 0.9) * size_factor
            
            # Unkraut-Typ
            weed_types = ['common_weed', 'grass_like', 'large_weed', 'tall_weed']
            weed_type = random.choice(weed_types)
            
            detection = {
                'class': 'weed',
                'subclass': weed_type,
                'confidence': round(confidence, 3),
                'bbox': {'x': x, 'y': y, 'width': width, 'height': height},
                'center': {'x': x + width//2, 'y': y + height//2},
                'area': width * height,
                'circularity': round(random.uniform(0.3, 0.8), 3),
                'aspect_ratio': round(height/width, 3),
                'perimeter': round(2 * (width + height), 1),
                'x': x + width//2,
                'y': y + height//2,
                'id': i + 1,
                'mock': True
            }
            
            detections.append(detection)
        
        return detections
    
    def _tensorflow_detection(self, image):
        """Platzhalter für TensorFlow-Erkennung"""
        self.log("🤖 TensorFlow-Erkennung noch nicht implementiert")
        return self._mock_detection(image)
    
    def _calculate_average_confidence(self, detections):
        """Durchschnittliche Confidence berechnen"""
        if not detections:
            return 0.0
        
        total_confidence = sum(d['confidence'] for d in detections)
        return round(total_confidence / len(detections), 3)
    
    def draw_detections(self, image, detections):
        """Erkennungen auf Bild zeichnen"""
        result_image = image.copy()
        
        for detection in detections:
            bbox = detection['bbox']
            confidence = detection['confidence']
            weed_type = detection.get('subclass', 'unknown')
            
            # Farbe basierend auf Confidence
            if confidence > 0.8:
                color = (0, 255, 0)  # Grün - hohe Confidence
            elif confidence > 0.6:
                color = (0, 255, 255)  # Gelb - mittlere Confidence
            else:
                color = (0, 165, 255)  # Orange - niedrige Confidence
            
            # Bounding Box
            cv2.rectangle(result_image, 
                         (bbox['x'], bbox['y']), 
                         (bbox['x'] + bbox['width'], bbox['y'] + bbox['height']), 
                         color, 2)
            
            # Zentrumskreis
            center = (detection['center']['x'], detection['center']['y'])
            cv2.circle(result_image, center, 5, color, -1)
            
            # Label mit Typ und Confidence
            label = f"{weed_type} {confidence:.2f}"
            cv2.putText(result_image, label, 
                       (bbox['x'], bbox['y'] - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        return result_image
    
    def update_settings(self, new_settings):
        """Einstellungen aktualisieren"""
        self.settings.update(new_settings)
        self.log(f"🔧 Einstellungen aktualisiert: {new_settings}")
    
    def change_green_profile(self, profile_name):
        """Grün-Profil wechseln"""
        if profile_name in self.green_profiles:
            self.current_profile = profile_name
            self.log(f"🎨 Grün-Profil gewechselt zu: {self.green_profiles[profile_name]['name']}")
        else:
            self.log(f"❌ Unbekanntes Profil: {profile_name}")
    
    def get_statistics(self):
        """Erkennungsstatistiken"""
        return {
            'total_detections': self.detection_count,
            'current_profile': self.green_profiles[self.current_profile]['name'],
            'settings': self.settings.copy(),
            'available_profiles': list(self.green_profiles.keys()),
            'model_loaded': self.model_loaded,
            'debug_mode': self.debug_mode
        }
