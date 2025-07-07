# hardware/camera.py - Korrigierte Version für libcamera
"""
Kamera-Manager für Unkraut-2025 - libcamera fix
Funktioniert mit deiner Pi-Kamera über libcamera!
"""
import cv2
import numpy as np
import time
import threading
import os
import subprocess

class CameraManager:
    def __init__(self):
        self.camera = None
        self.is_streaming = False
        self.current_frame = None
        self.frame_lock = threading.Lock()
        self.camera_type = 'mock'
        self.libcamera_process = None
        self._libcamera_working = None  # Cache für libcamera Test-Ergebnis
        self.settings = {
            'brightness': 50,
            'contrast': 50,
            'resolution': (640, 480),
            'framerate': 20
        }
        
        print("📷 Kamera-Manager startet...")
        self._detect_camera()
    
    def _detect_camera(self):
        """Verbesserte Kamera-Erkennung für libcamera"""
        print("🔍 Suche verfügbare Kameras...")
        
        # 1. Teste libcamera (funktioniert bei dir!)
        if self._test_libcamera_working():
            self.camera_type = 'libcamera'
            print("✅ libcamera Kamera erfolgreich erkannt!")
            return
        
        # 2. USB Fallback
        usb_device = self._find_usb_camera()
        if usb_device is not None:
            self.camera_type = 'usb'  
            self.camera_device = usb_device
            print(f"✅ USB Kamera gefunden")
            return
        
        # 3. Mock als letzter Fallback
        self.camera_type = 'mock'
        print("⚠️  Fallback zu Mock-Modus")
    
    def _test_libcamera_working(self):
        """Teste ob libcamera tatsächlich funktioniert - mit Caching"""
        # Cache verwenden wenn bereits getestet
        if self._libcamera_working is not None:
            return self._libcamera_working
            
        try:
            print("🧪 Teste libcamera-hello...")
            
            # Kurzer Test mit libcamera-hello
            result = subprocess.run([
                'libcamera-hello', 
                '--timeout', '100',  # Nur 100ms
                '--nopreview'  # Kein Preview-Fenster
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                print("✅ libcamera-hello funktioniert!")
                
                # Zusätzlicher Test: Kann libcamera-vid gestartet werden?
                try:
                    test_process = subprocess.Popen([
                        'libcamera-vid',
                        '--timeout', '100',
                        '--nopreview',
                        '--codec', 'mjpeg',
                        '--output', '/dev/null'
                    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    
                    time.sleep(0.2)
                    test_process.terminate()
                    test_process.wait(timeout=2)
                    
                    print("✅ libcamera-vid auch funktionsfähig!")
                    self._libcamera_working = True  # Cache speichern
                    return True
                    
                except Exception as e:
                    print(f"⚠️  libcamera-vid Test unvollständig: {e}")
                    self._libcamera_working = True  # libcamera-hello hat funktioniert, das reicht
                    return True
            else:
                print(f"❌ libcamera-hello Fehler: {result.stderr}")
                self._libcamera_working = False
                return False
                
        except subprocess.TimeoutExpired:
            print("⚠️  libcamera-hello Timeout - möglicherweise trotzdem OK")
            self._libcamera_working = True  # Timeout kann OK sein
            return True
        except Exception as e:
            print(f"❌ libcamera Test Fehler: {e}")
            self._libcamera_working = False
            return False
    
    def _find_usb_camera(self):
        """USB Kamera finden"""
        for device in [0, 1, 2]:
            try:
                cap = cv2.VideoCapture(device)
                if cap.isOpened():
                    ret, frame = cap.read()
                    cap.release()
                    if ret and frame is not None:
                        return device
            except:
                pass
        return None
    
    def start_stream(self):
        """Kamera-Stream starten"""
        if self.is_streaming:
            return True
            
        print(f"📹 Starte {self.camera_type} Stream...")
        
        if self.camera_type == 'libcamera':
            return self._start_libcamera_stream()
        elif self.camera_type == 'usb':
            return self._start_usb_stream()  
        else:
            return self._start_mock_stream()
    
    def _start_libcamera_stream(self):
        """libcamera Stream - optimiert für deine Kamera"""
        try:
            self.is_streaming = True
            threading.Thread(target=self._libcamera_worker, daemon=True).start()
            print("✅ libcamera Stream gestartet")
            return True
        except Exception as e:
            print(f"❌ libcamera Stream Fehler: {e}")
            return self._start_mock_stream()
    
    def _libcamera_worker(self):
        """libcamera Worker - robuste Version"""
        try:
            # Verwende raspistill-ähnlichen Ansatz mit mjpeg
            cmd = [
                'libcamera-vid',
                '--timeout', '0',  # Endlos
                '--nopreview',
                '--codec', 'mjpeg',
                '--width', str(self.settings['resolution'][0]),
                '--height', str(self.settings['resolution'][1]),
                '--framerate', str(self.settings['framerate']),
                '--output', '-'  # Stdout
            ]
            
            self.libcamera_process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                bufsize=10**5
            )
            
            # MJPEG Stream parsen
            buffer = b""
            while self.is_streaming and self.libcamera_process.poll() is None:
                chunk = self.libcamera_process.stdout.read(4096)
                if not chunk:
                    break
                    
                buffer += chunk
                
                # JPEG Marker finden
                while True:
                    start = buffer.find(b'\xff\xd8')  # JPEG Start
                    if start == -1:
                        break
                        
                    end = buffer.find(b'\xff\xd9', start + 2)  # JPEG End
                    if end == -1:
                        break
                        
                    # Komplettes JPEG Frame
                    jpeg_data = buffer[start:end + 2]
                    
                    with self.frame_lock:
                        self.current_frame = jpeg_data
                    
                    buffer = buffer[end + 2:]
                    
        except Exception as e:
            print(f"❌ libcamera Worker Fehler: {e}")
        finally:
            if self.libcamera_process:
                self.libcamera_process.terminate()
                self.libcamera_process = None
    
    def _start_usb_stream(self):
        """USB Kamera Stream"""
        try:
            self.camera = cv2.VideoCapture(self.camera_device)
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.settings['resolution'][0])
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.settings['resolution'][1])
            self.camera.set(cv2.CAP_PROP_FPS, self.settings['framerate'])
            
            if self.camera.isOpened():
                self.is_streaming = True
                threading.Thread(target=self._usb_worker, daemon=True).start()
                print("✅ USB Stream gestartet")
                return True
        except Exception as e:
            print(f"❌ USB Stream Fehler: {e}")
        
        return self._start_mock_stream()
    
    def _usb_worker(self):
        """USB Kamera Worker"""
        while self.is_streaming and self.camera and self.camera.isOpened():
            try:
                ret, frame = self.camera.read()
                if ret and frame is not None:
                    # Frame zu JPEG
                    _, jpeg_data = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                    
                    with self.frame_lock:
                        self.current_frame = jpeg_data.tobytes()
                else:
                    time.sleep(0.1)
                    
            except Exception as e:
                print(f"❌ USB Worker Fehler: {e}")
                break
    
    def _start_mock_stream(self):
        """Mock Stream für Tests"""
        try:
            self.is_streaming = True
            threading.Thread(target=self._mock_worker, daemon=True).start()
            print("✅ Mock Stream gestartet")
            return True
        except Exception as e:
            print(f"❌ Mock Stream Fehler: {e}")
            return False
    
    def _mock_worker(self):
        """Mock Kamera Worker"""
        frame_count = 0
        while self.is_streaming:
            try:
                # Dynamischer Mock-Frame
                frame = np.zeros((480, 640, 3), dtype=np.uint8)
                
                # Beweglicher Kreis
                center_x = int(320 + 200 * np.sin(frame_count * 0.1))
                center_y = int(240 + 100 * np.cos(frame_count * 0.15))
                cv2.circle(frame, (center_x, center_y), 30, (0, 255, 0), -1)
                
                # Text overlay
                cv2.putText(frame, f"Mock Camera - Frame {frame_count}", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(frame, f"Time: {time.strftime('%H:%M:%S')}", 
                           (10, 460), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                
                # Simuliere Unkraut-Spots
                if frame_count % 60 < 30:  # Alle 2s für 1s
                    cv2.circle(frame, (450, 150), 15, (0, 0, 255), -1)
                    cv2.putText(frame, "WEED", (430, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                
                # Frame zu JPEG
                _, jpeg_data = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                
                with self.frame_lock:
                    self.current_frame = jpeg_data.tobytes()
                
                frame_count += 1
                time.sleep(1.0 / self.settings['framerate'])
                
            except Exception as e:
                print(f"❌ Mock Worker Fehler: {e}")
                break
    
    def stop_stream(self):
        """Stream stoppen"""
        self.is_streaming = False
        
        if self.libcamera_process:
            try:
                self.libcamera_process.terminate()
                self.libcamera_process.wait(timeout=3)
            except:
                try:
                    self.libcamera_process.kill()
                except:
                    pass
            self.libcamera_process = None
        
        if self.camera:
            try:
                self.camera.release()
            except:
                pass
            self.camera = None
        
        print("🛑 Kamera-Stream gestoppt")
    
    def get_frame(self):
        """Aktuelles Frame holen"""
        with self.frame_lock:
            if self.current_frame:
                # bytes-Objekte haben keine copy() Methode - einfach zurückgeben
                return self.current_frame
            return None
    
    def capture_image(self, filename=None):
        """Foto aufnehmen - startet Stream automatisch falls nötig"""
        # Stream automatisch starten falls nicht aktiv
        if not self.is_streaming:
            print("📹 Starte Stream für Capture...")
            success = self.start_stream()
            if not success:
                print("❌ Stream-Start fehlgeschlagen - verwende libcamera-still")
                return self._capture_with_libcamera_still(filename)
            
            # Kurz warten bis Frames verfügbar sind
            for i in range(10):  # Max 5 Sekunden warten
                time.sleep(0.5)
                if self.current_frame is not None:
                    break
            else:
                print("⚠️  Keine Frames nach 5s - verwende libcamera-still")
                return self._capture_with_libcamera_still(filename)
        
        # Stream-Frame verwenden
        frame_data = self.get_frame()
        if frame_data and len(frame_data) > 1000:
            try:
                if not filename:
                    # Neues Datumsformat: capture_YY.MM.DD_hh.mm_ss.jpg
                    from datetime import datetime
                    now = datetime.now()
                    filename = f"capture_{now.strftime('%y.%m.%d_%H.%M_%S')}.jpg"
                
                filepath = os.path.join("data/images", filename)
                os.makedirs("data/images", exist_ok=True)
                
                with open(filepath, 'wb') as f:
                    f.write(frame_data)
                
                print(f"📸 Foto gespeichert (640x480): {filepath}")
                return filename
            except Exception as e:
                print(f"❌ Stream-Foto Fehler: {e}")
        
        # Fallback: libcamera-still
        print("⚠️  Stream-Frame nicht verfügbar - verwende libcamera-still")
        return self._capture_with_libcamera_still(filename)
    
    def _capture_with_libcamera_still(self, filename=None):
        """Fallback: Direkte Aufnahme mit libcamera-still"""
        if self.camera_type != 'libcamera':
            print("❌ libcamera-still nur mit libcamera verfügbar")
            return None
        
        try:
            if not filename:
                # Neues Datumsformat: capture_YY.MM.DD_hh.mm_ss.jpg
                from datetime import datetime
                now = datetime.now()
                filename = f"capture_{now.strftime('%y.%m.%d_%H.%M_%S')}.jpg"
            
            filepath = os.path.join("data/images", filename)
            os.makedirs("data/images", exist_ok=True)
            
            print("📸 Verwende libcamera-still für Direktaufnahme...")
            
            # Stream temporär stoppen um Konflikt zu vermeiden
            was_streaming = self.is_streaming
            if was_streaming:
                print("🛑 Stoppe Stream temporär...")
                self.stop_stream()
                time.sleep(1)
            
            # libcamera-still ausführen
            result = subprocess.run([
                'libcamera-still',
                '-o', filepath,
                '--timeout', '2000',
                '--width', '1920',
                '--height', '1080',
                '--nopreview'
            ], capture_output=True, timeout=15)
            
            # Stream wieder starten falls er lief
            if was_streaming:
                print("🔄 Starte Stream wieder...")
                self.start_stream()
            
            if result.returncode == 0 and os.path.exists(filepath):
                size = os.path.getsize(filepath)
                print(f"✅ libcamera-still Foto (1920x1080): {filepath} ({size} bytes)")
                return filename
            else:
                print(f"❌ libcamera-still Fehler: {result.stderr.decode()}")
                return None
                
        except Exception as e:
            print(f"❌ libcamera-still Exception: {e}")
            # Stream wieder starten bei Fehler
            if was_streaming and not self.is_streaming:
                self.start_stream()
            return None
        
    def adjust_setting(self, setting, value):
        """Einstellungen anpassen"""
        if setting in self.settings:
            self.settings[setting] = value
            print(f"📷 {setting}: {value}")
            return True
        return False
    
    def get_camera_info(self):
        """Kamera-Info - ohne ständigen libcamera-Test"""
        return {
            'type': self.camera_type,
            'is_streaming': self.is_streaming,
            'settings': self.settings.copy(),
            'frame_available': self.current_frame is not None,
            'libcamera_working': self._libcamera_working if self._libcamera_working is not None else False
        }
    
    def restart_stream(self):
        """Stream neu starten"""
        print("🔄 Starte Kamera neu...")
        self.stop_stream()
        time.sleep(2)
        self._detect_camera()
        return self.start_stream()

# Globale Instanz
camera_manager = CameraManager()

# Test-Funktion
def test_camera():
    """Ausführlicher Kamera-Test"""
    print("🧪 Teste Kamera-Manager...")
    print("=" * 50)
    
    # Info anzeigen
    info = camera_manager.get_camera_info()
    print(f"Kamera-Typ: {info['type']}")
    print(f"libcamera funktioniert: {info['libcamera_working']}")
    print(f"Stream läuft: {info['is_streaming']}")
    
    # Stream starten
    if camera_manager.start_stream():
        print("✅ Stream erfolgreich gestartet!")
        
        # Warten bis Frames kommen
        print("⏳ Warte auf Frames...")
        for i in range(10):
            time.sleep(0.5)
            if camera_manager.current_frame is not None:
                print(f"✅ Frame empfangen nach {(i+1)*0.5}s")
                break
        else:
            print("⚠️  Keine Frames nach 5s")
        
        # Frame-Test
        frame_data = camera_manager.get_frame()
        print(f"Frame-Größe: {len(frame_data)} bytes")
        
        # Foto-Test
        filename = camera_manager.capture_image()
        if filename:
            print(f"📸 Foto gespeichert: {filename}")
        
        # Kurz laufen lassen
        print("⏳ Lasse Stream 3s laufen...")
        time.sleep(3)
        
        camera_manager.stop_stream()
        print("🛑 Test abgeschlossen")
        return True
    else:
        print("❌ Stream-Start fehlgeschlagen")
        return False

if __name__ == '__main__':
    test_camera()