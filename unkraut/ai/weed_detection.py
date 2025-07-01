"""
Unkraut-Erkennung (Mock-Version)
"""
import time
import random
import numpy as np

class WeedDetector:
    def __init__(self):
        self.classes = ['Gras', 'Unkraut', 'Löwenzahn', 'Klee']
        print("🧠 Mock-WeedDetector initialisiert")
    
    def load_model(self):
        print("✅ Mock-Model geladen")
        return True
    
    def detect_from_bytes(self, image_bytes):
        time.sleep(0.1)  # Simuliere Verarbeitung
        
        # Mock-Detektionen
        num_detections = random.randint(0, 3)
        detections = []
        
        for i in range(num_detections):
            detections.append({
                'id': i,
                'class': random.choice(self.classes),
                'confidence': random.uniform(0.6, 0.95),
                'x': random.randint(10, 80),
                'y': random.randint(10, 80),
                'width': random.randint(10, 30),
                'height': random.randint(10, 30)
            })
        
        avg_confidence = sum(d['confidence'] for d in detections) / len(detections) if detections else 0
        
        return {
            'status': 'success',
            'detections': detections,
            'confidence': avg_confidence,
            'processing_time': 0.1
        }

# Globale Instanz
weed_detector = WeedDetector()
