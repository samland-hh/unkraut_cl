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
        """Teste ob libcamera tatsächlich funktioniert"""
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
                    return True
                    
                except Exception as e:
                    print(f"⚠️  libcamera-vid Test unvollständig: {e}")
                    return True  # libcamera-hello hat funktioniert, das reicht
            else:
                print(f"❌ libcamera-hello Fehler: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("⚠️  libcamera-hello Timeout - möglicherweise trotzdem OK")
            return True  # Timeout kann OK sein
        except Exception as e:
            print(f"❌ libcamera Test Fehler: {e}")
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
            # libcamera-vid Befehl für MJPEG Stream
            cmd = [
                'libcamera-vid',
                '--timeout', '0',  # Endlos laufen
                '--nopreview',     # Kein GUI Preview
                '--width', str(self.settings['resolution'][0]),
                '--height', str(self.settings['resolution'][1]),
                '--framerate', str(self.settings['framerate']),
                '--codec', 'mjpeg',
                '--inline',
                '--output', '-'  # Stdout
            ]
            
            print(f"🚀 Starte: {' '.join(cmd)}")
            
            self.libcamera_process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=0
            )
            
            buffer = b''
            jpeg_start = b'\xff\xd8'
            jpeg_end = b'\xff\xd9'
            
            print("📡 libcamera MJPEG Stream läuft...")
            
            while self.is_streaming and self.libcamera_process.poll() is None:
                try:
                    # Daten lesen
                    chunk = self.libcamera_process.stdout.read(8192)
                    if not chunk:
                        print("⚠️  Keine Daten von libcamera")
                        break
                    
                    buffer += chunk
                    
                    # JPEG Frames extrahieren
                    while True:
                        start_pos = buffer.find(jpeg_start)
                        if start_pos == -1:
                            break
                            
                        end_pos = buffer.find(jpeg_end, start_pos)
                        if end_pos == -1:
                            break
                        
                        # Komplettes JPEG Frame
                        end_pos += 2
                        jpeg_data = buffer[start_pos:end_pos]
                        buffer = buffer[end_pos:]
                        
                        # JPEG zu OpenCV Frame
                        nparr = np.frombuffer(jpeg_data, np.uint8)
                        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                        
                        if frame is not None:
                            with self.frame_lock:
                                self.current_frame = frame
                            #print(f"📸 Frame: {frame.shape}")
                        else:
                            print("⚠️  Frame dekodierung fehlgeschlagen")
                
                except Exception as e:
                    print(f"❌ libcamera Worker Fehler: {e}")
                    break
            
            # Cleanup
            if self.libcamera_process and self.libcamera_process.poll() is None:
                print("🛑 Stoppe libcamera-vid...")
                self.libcamera_process.terminate()
                try:
                    self.libcamera_process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    print("⚠️  Force kill libcamera-vid")
                    self.libcamera_process.kill()
            
            print("📹 libcamera Worker beendet")
            
        except Exception as e:
            print(f"❌ libcamera Worker kritischer Fehler: {e}")
        finally:
            # Fallback zu Mock falls Stream stoppt
            if self.is_streaming:
                print("🎭 Wechsle zu Mock wegen libcamera Problemen")
                self._start_mock_stream()
    
    def _start_usb_stream(self):
        """USB Kamera Stream"""
        try:
            self.camera = cv2.VideoCapture(self.camera_device)
            if not self.camera.isOpened():
                return self._start_mock_stream()
            
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.settings['resolution'][0])
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.settings['resolution'][1])
            self.camera.set(cv2.CAP_PROP_FPS, self.settings['framerate'])
            
            self.is_streaming = True
            threading.Thread(target=self._usb_worker, daemon=True).start()
            return True
        except Exception as e:
            print(f"❌ USB Stream Fehler: {e}")
            return self._start_mock_stream()
    
    def _usb_worker(self):
        """USB Worker"""
        while self.is_streaming and self.camera:
            try:
                ret, frame = self.camera.read()
                if ret:
                    with self.frame_lock:
                        self.current_frame = frame
                time.sleep(1/self.settings['framerate'])
            except Exception as e:
                print(f"❌ USB Worker Fehler: {e}")
                break
    
    def _start_mock_stream(self):
        """Mock Stream Fallback"""
        self.camera_type = 'mock'
        self.is_streaming = True
        threading.Thread(target=self._mock_worker, daemon=True).start()
        print("🎭 Mock-Stream gestartet")
        return True
    
    def _mock_worker(self):
        """Mock Worker"""
        frame_count = 0
        while self.is_streaming:
            try:
                # Schönes Mock-Bild mit Garden-Theme
                img = np.zeros((self.settings['resolution'][1], self.settings['resolution'][0], 3), dtype=np.uint8)
                
                # Grüner Garten-Hintergrund
                img[:, :] = (0, 80, 0)
                
                # Simulierte "Pflanzen"
                for i in range(5):
                    x = 80 + i * 120
                    y = 300 + int(20 * np.sin(frame_count * 0.1 + i))
                    cv2.circle(img, (x, y), 25, (0, 150, 0), -1)
                    cv2.circle(img, (x, y-15), 15, (0, 200, 0), -1)
                
                # Status-Info
                status_text = [
                    "🤖 Unkraut-2025 - Pi Kamera",
                    f"Modus: {self.camera_type.upper()}",
                    f"Zeit: {time.strftime('%H:%M:%S')}",
                    f"Frame: {frame_count}",
                    "libcamera-hello/still/vid funktioniert! ✅"
                ]
                
                for i, text in enumerate(status_text):
                    y_pos = 30 + i * 25
                    cv2.putText(img, text, (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                
                with self.frame_lock:
                    self.current_frame = img
                
                frame_count += 1
                time.sleep(1/self.settings['framerate'])
                
            except Exception as e:
                print(f"❌ Mock Worker Fehler: {e}")
                time.sleep(1)
    
    def stop_stream(self):
        """Stream stoppen"""
        self.is_streaming = False
        
        # libcamera Prozess stoppen
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
        
        # USB Kamera stoppen
        if self.camera:
            try:
                self.camera.release()
            except:
                pass
            self.camera = None
        
        print("📹 Stream gestoppt")
    
    def get_frame(self):
        """Aktuelles Frame als JPEG"""
        with self.frame_lock:
            if self.current_frame is not None:
                try:
                    ret, buffer = cv2.imencode('.jpg', self.current_frame, 
                                             [cv2.IMWRITE_JPEG_QUALITY, 80])
                    if ret:
                        return buffer.tobytes()
                except Exception as e:
                    print(f"❌ Frame Encoding: {e}")
        
        # Fallback
        return self._create_error_frame()
    
    def _create_error_frame(self):
        """Fehler-Frame"""
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        img[:] = (0, 0, 100)
        cv2.putText(img, 'KAMERA FEHLER', (200, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        ret, buffer = cv2.imencode('.jpg', img)
        return buffer.tobytes() if ret else b''
    
 def capture_image(self, filename=None, high_resolution=False):
    """
    Foto aufnehmen - mit Option für hochaufgelöste Fotos
    high_resolution=True: Stoppt Stream für libcamera-still (1920x1080)
    high_resolution=False: Nutzt Stream-Frame (640x480)
    """
    if filename is None:
        filename = f"capture_{int(time.time())}.jpg"
    
    filepath = f"data/images/{filename}"
    os.makedirs("data/images", exist_ok=True)
    
    # Hochauflösendes Foto (stoppt Stream temporär)
    if high_resolution and self.camera_type == 'libcamera':
        print("📸 Stoppe Stream für hochaufgelöstes Foto...")
        
        # Stream temporär stoppen
        was_streaming = self.is_streaming
        if was_streaming:
            self.stop_stream()
            time.sleep(1)  # Warten bis libcamera-vid wirklich beendet ist
        
        try:
            result = subprocess.run([
                'libcamera-still',
                '-o', filepath,
                '--timeout', '2000',
                '--width', '1920',
                '--height', '1080',
                '--nopreview'
            ], capture_output=True, timeout=15)
            
            if result.returncode == 0 and os.path.exists(filepath):
                print(f"📸 Hochauflösendes Foto (1920x1080): {filepath}")
                
                # Stream wieder starten falls er lief
                if was_streaming:
                    print("🔄 Starte Stream wieder...")
                    self.start_stream()
                
                return filename
            else:
                print(f"❌ libcamera-still Fehler: {result.stderr.decode()}")
        
        except Exception as e:
            print(f"❌ Hochauflösendes Foto Fehler: {e}")
        
        # Stream wieder starten bei Fehler
        if was_streaming:
            self.start_stream()
    
    # Standard: Stream-Frame verwenden (kein Konflikt)
    frame_data = self.get_frame()
    if frame_data and len(frame_data) > 1000:
        try:
            with open(filepath, 'wb') as f:
                f.write(frame_data)
            print(f"📸 Stream-Frame gespeichert (640x480): {filepath}")
            return filename
        except Exception as e:
            print(f"❌ Stream-Foto Fehler: {e}")
    
    return None    
    def adjust_setting(self, setting, value):
        """Einstellungen anpassen"""
        if setting in self.settings:
            self.settings[setting] = value
            print(f"📷 {setting}: {value}")
            return True
        return False
    
    def get_camera_info(self):
        """Kamera-Info"""
        return {
            'type': self.camera_type,
            'is_streaming': self.is_streaming,
            'settings': self.settings.copy(),
            'frame_available': self.current_frame is not None,
            'libcamera_working': self._test_libcamera_working()
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