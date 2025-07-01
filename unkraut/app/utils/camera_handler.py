"""
Kamera-Handler für Flask
"""
from hardware.camera import camera_manager
import time

class CameraHandler:
    def __init__(self):
        self.camera_manager = camera_manager
    
    def get_video_stream(self):
        self.camera_manager.start_stream()
        
        while True:
            frame = self.camera_manager.get_frame()
            if frame:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(0.033)
    
    def capture_image(self, filename=None):
        return self.camera_manager.capture_image(filename)
    
    def adjust_camera(self, setting, value):
        return self.camera_manager.adjust_setting(setting, value)

# Globale Instanz
camera_handler = CameraHandler()
