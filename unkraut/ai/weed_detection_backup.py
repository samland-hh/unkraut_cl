# ai/weed_detection.py
"""
KI-basierte Unkrauterkennung für Unkraut-2025
Unterstützt OpenCV und TensorFlow mit Mock-Fallback
"""
import cv2
import numpy as np
import time
import random
from datetime import datetime

class WeedDetector:
    def __init__(self):
        self.model_loaded = False
        self.model = None
        self.confidence_threshold = 0.5
        self.detection_count = 0
        self.init_ai_model()
    
    def init_ai_model(self):
        """KI-Modell initialisieren"""
        try:
            # Versuche TensorFlow zu laden
            import tensorflow as tf
            
            # Hier würde normalerweise ein trainiertes Modell geladen werden
            # model_path = 'ai/models/weed_detection_model.h5'
            # self.model = tf.keras.models.load_model(model_path)
            
            print("⚠️ Kein trainiertes Modell gefunden")
            print("💡 Verwende OpenCV-basierte Erkennung + Mock")
            self._init_opencv_detection()
            
        except ImportError:
            print("⚠️ TensorFlow nicht installiert")
            print("💡 Install: pip install tensorflow")
            self._init_opencv_detection()
        except Exception as e:
            print(f"⚠️ KI-Modell-Initialisierung fehlgeschlagen: {e}")
            self._init_opencv_detection()
    
    def _init_opencv_detection(self):
        """OpenCV-basierte Grunderkennung"""
        self.model_loaded = False
        print("🔧 OpenCV + Mock-Erkennung aktiviert")
    
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
        """Unkraut in OpenCV-Bild erkennen"""
        start_time = time.time()
        
        try:
            if self.model_loaded and self.model:
                # TensorFlow-Modell verwenden
                detections = self._tensorflow_detection(image)
            else:
                # OpenCV + Mock-Erkennung
                detections = self._opencv_detection(image)
            
            processing_time = time.time() - start_time
            self.detection_count += 1
            
            # Ergebnis zusammenstellen
            result = {
                'detections': detections,
                'count': len(detections),
                'confidence': self._calculate_average_confidence(detections),
                'processing_time': round(processing_time, 3),
                'timestamp': int(time.time()),
                'detection_id': self.detection_count,
                'image_size': {'width': image.shape[1], 'height': image.shape[0]},
                'method': 'tensorflow' if self.model_loaded else 'opencv_mock'
            }
            
            return result
            
        except Exception as e:
            return {
                'error': str(e),
                'detections': [],
                'count': 0,
                'processing_time': time.time() - start_time
            }
    
    def _tensorflow_detection(self, image):
        """TensorFlow-basierte Erkennung"""
        # Hier würde das echte TensorFlow-Modell verwendet werden
        # Für jetzt Mock-Implementierung
        return self._mock_detection(image)
    
    def _opencv_detection(self, image):
        """OpenCV-basierte Grunderkennung"""
        detections = []
        
        try:
            # Zu HSV konvertieren für bessere Farberkennung
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Grün-Bereiche erkennen (mögliche Vegetation)
            lower_green = np.array([35, 40, 40])
            upper_green = np.array([85, 255, 255])
            green_mask = cv2.inRange(hsv, lower_green, upper_green)
            
            # Morphological Operations für bessere Erkennung
            kernel = np.ones((5,5), np.uint8)
            green_mask = cv2.morphologyEx(green_mask, cv2.MORPH_CLOSE, kernel)
            green_mask = cv2.morphologyEx(green_mask, cv2.MORPH_OPEN, kernel)
            
            # Konturen finden
            contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Große Konturen als potentielle Unkräuter klassifizieren
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 500:  # Mindestgröße
                    # Bounding Box
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # Zentrum berechnen
                    center_x = x + w // 2
                    center_y = y + h // 2
                    
                    # Confidence basierend auf Größe und Form
                    confidence = min(0.9, area / 5000)
                    
                    detection = {
                        'class': 'weed',
                        'confidence': round(confidence, 2),
                        'bbox': {'x': x, 'y': y, 'width': w, 'height': h},
                        'center': {'x': center_x, 'y': center_y},
                        'area': int(area),
                        'x': center_x,  # Für Roboterarm-Koordinaten
                        'y': center_y
                    }
                    
                    detections.append(detection)
            
            # Sortiere nach Confidence
            detections.sort(key=lambda x: x['confidence'], reverse=True)
            
            # Maximal 5 Erkennungen zurückgeben
            return detections[:5]
            
        except Exception as e:
            print(f"OpenCV-Erkennung fehlgeschlagen: {e}")
            return self._mock_detection(image)
    
    def _mock_detection(self, image):
        """Mock-Erkennung für Tests"""
        detections = []
        
        # Zufällige Anzahl von Erkennungen (0-3)
        num_detections = random.randint(0, 3)
        
        h, w = image.shape[:2]
        
        for i in range(num_detections):
            # Zufällige Position
            x = random.randint(50, w - 100)
            y = random.randint(50, h - 80)
            width = random.randint(30, 80)
            height = random.randint(30, 80)
            
            # Zufällige Confidence
            confidence = random.uniform(0.6, 0.95)
            
            detection = {
                'class': 'weed',
                'confidence': round(confidence, 2),
                'bbox': {'x': x, 'y': y, 'width': width, 'height': height},
                'center': {'x': x + width//2, 'y': y + height//2},
                'area': width * height,
                'x': x + width//2,
                'y': y + height//2,
                'mock': True
            }
            
            detections.append(detection)
        
        return detections
    
    def _calculate_average_confidence(self, detections):
        """Durchschnittliche Confidence berechnen"""
        if not detections:
            return 0.0
        
        total_confidence = sum(d['confidence'] for d in detections)
        return round(total_confidence / len(detections), 2)
    
    def draw_detections(self, image, detections):
        """Erkennungen auf Bild zeichnen"""
        result_image = image.copy()
        
        for detection in detections:
            bbox = detection['bbox']
            confidence = detection['confidence']
            
            # Bounding Box zeichnen
            color = (0, 255, 0) if confidence > 0.7 else (0, 255, 255)
            cv2.rectangle(result_image, 
                         (bbox['x'], bbox['y']), 
                         (bbox['x'] + bbox['width'], bbox['y'] + bbox['height']), 
                         color, 2)
            
            # Label
            label = f"Weed {confidence:.2f}"
            cv2.putText(result_image, label, 
                       (bbox['x'], bbox['y'] - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            # Zentrum markieren
            center = detection['center']
            cv2.circle(result_image, (center['x'], center['y']), 3, (0, 0, 255), -1)
        
        return result_image
    
    def save_detection_result(self, image, detections, filename=None):
        """Erkennungsergebnis speichern"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data/images/detection_{timestamp}_{len(detections)}_weeds.jpg"
        
        try:
            import os
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            result_image = self.draw_detections(image, detections)
            cv2.imwrite(filename, result_image)
            
            print(f"💾 Erkennungsergebnis gespeichert: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Speichern fehlgeschlagen: {e}")
            return None
    
    def get_detection_stats(self):
        """Erkennungsstatistiken"""
        return {
            'total_detections': self.detection_count,
            'model_loaded': self.model_loaded,
            'confidence_threshold': self.confidence_threshold,
            'method': 'tensorflow' if self.model_loaded else 'opencv_mock'
        }
    
    def set_confidence_threshold(self, threshold):
        """Confidence-Schwellwert setzen"""
        self.confidence_threshold = max(0.1, min(0.9, threshold))
        print(f"🎯 Confidence-Schwellwert: {self.confidence_threshold}")

# Globale Instanz
weed_detector = WeedDetector()