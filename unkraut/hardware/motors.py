# hardware/motors.py
"""
Motor-Controller für Unkraut-2025 Fahrzeug
Unterstützt GPIO-Motoren mit Mock-Fallback
"""
import time
import threading

class MotorController:
    def __init__(self):
        self.gpio_available = False
        self.is_moving = False
        self.current_direction = None
        self.current_speed = 0
        self.emergency_stopped = False
        
        # Motor-Pin-Konfiguration (Beispiel für L298N)
        self.motor_pins = {
            'left_motor': {
                'forward': 18,
                'backward': 19,
                'enable': 12  # PWM Pin
            },
            'right_motor': {
                'forward': 20,
                'backward': 21,
                'enable': 13  # PWM Pin
            }
        }
        
        self.init_hardware()
    
    def init_hardware(self):
        """GPIO Hardware initialisieren"""
        try:
            import RPi.GPIO as GPIO
            
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            
            # Motor-Pins als Output konfigurieren
            for motor, pins in self.motor_pins.items():
                GPIO.setup(pins['forward'], GPIO.OUT)
                GPIO.setup(pins['backward'], GPIO.OUT)
                GPIO.setup(pins['enable'], GPIO.OUT)
                
                # PWM für Geschwindigkeitssteuerung
                setattr(self, f'{motor}_pwm', GPIO.PWM(pins['enable'], 1000))  # 1kHz
                getattr(self, f'{motor}_pwm').start(0)
            
            self.gpio_available = True
            print("✅ Motor-Hardware initialisiert (GPIO)")
            
        except ImportError:
            print("⚠️ RPi.GPIO nicht verfügbar")
            self._init_mock_mode()
        except Exception as e:
            print(f"⚠️ GPIO-Initialisierung fehlgeschlagen: {e}")
            self._init_mock_mode()
    
    def _init_mock_mode(self):
        """Mock-Modus für Entwicklung ohne Hardware"""
        self.gpio_available = False
        print("🔧 Motor Mock-Modus aktiviert")
    
    def move(self, direction, speed=50, duration=0.1):
        """Fahrzeug bewegen"""
        if self.emergency_stopped:
            return {'error': 'Emergency stop active'}
        
        # Parameter validieren
        speed = max(0, min(100, speed))
        direction = direction.lower()
        
        if direction not in ['forward', 'backward', 'left', 'right', 'stop']:
            return {'error': f'Invalid direction: {direction}'}
        
        self.current_direction = direction
        self.current_speed = speed
        self.is_moving = direction != 'stop'
        
        if self.gpio_available:
            self._move_hardware(direction, speed)
        else:
            self._move_mock(direction, speed)
        
        # Automatisch stoppen nach duration
        if duration > 0 and direction != 'stop':
            threading.Timer(duration, self.stop).start()
        
        return {
            'status': 'success',
            'direction': direction,
            'speed': speed,
            'duration': duration,
            'hardware': self.gpio_available
        }
    
    def _move_hardware(self, direction, speed):
        """Hardware-Bewegung"""
        try:
            import RPi.GPIO as GPIO
            
            # PWM-Wert berechnen (0-100%)
            pwm_value = speed
            
            if direction == 'forward':
                self._set_motor_direction('left_motor', 'forward')
                self._set_motor_direction('right_motor', 'forward')
                self._set_motor_speed('left_motor', pwm_value)
                self._set_motor_speed('right_motor', pwm_value)
                
            elif direction == 'backward':
                self._set_motor_direction('left_motor', 'backward')
                self._set_motor_direction('right_motor', 'backward')
                self._set_motor_speed('left_motor', pwm_value)
                self._set_motor_speed('right_motor', pwm_value)
                
            elif direction == 'left':
                self._set_motor_direction('left_motor', 'backward')
                self._set_motor_direction('right_motor', 'forward')
                self._set_motor_speed('left_motor', pwm_value)
                self._set_motor_speed('right_motor', pwm_value)
                
            elif direction == 'right':
                self._set_motor_direction('left_motor', 'forward')
                self._set_motor_direction('right_motor', 'backward')
                self._set_motor_speed('left_motor', pwm_value)
                self._set_motor_speed('right_motor', pwm_value)
                
            elif direction == 'stop':
                self._stop_all_motors()
            
            print(f"🚗 Hardware: {direction} @ {speed}%")
            
        except Exception as e:
            print(f"❌ Hardware-Bewegung fehlgeschlagen: {e}")
    
    def _set_motor_direction(self, motor, direction):
        """Motor-Richtung setzen"""
        import RPi.GPIO as GPIO
        pins = self.motor_pins[motor]
        
        if direction == 'forward':
            GPIO.output(pins['forward'], GPIO.HIGH)
            GPIO.output(pins['backward'], GPIO.LOW)
        elif direction == 'backward':
            GPIO.output(pins['forward'], GPIO.LOW)
            GPIO.output(pins['backward'], GPIO.HIGH)
        else:
            GPIO.output(pins['forward'], GPIO.LOW)
            GPIO.output(pins['backward'], GPIO.LOW)
    
    def _set_motor_speed(self, motor, speed):
        """Motor-Geschwindigkeit setzen"""
        pwm = getattr(self, f'{motor}_pwm')
        pwm.ChangeDutyCycle(speed)
    
    def _stop_all_motors(self):
        """Alle Motoren stoppen"""
        for motor in self.motor_pins:
            self._set_motor_direction(motor, 'stop')
            self._set_motor_speed(motor, 0)
    
    def _move_mock(self, direction, speed):
        """Mock-Bewegung für Tests"""
        print(f"🔧 Mock: {direction} @ {speed}%")
        
        # Simulierte Latenz
        time.sleep(0.01)
    
    def stop(self):
        """Fahrzeug stoppen"""
        self.current_direction = 'stop'
        self.current_speed = 0
        self.is_moving = False
        
        if self.gpio_available:
            self._stop_all_motors()
            print("🛑 Hardware gestoppt")
        else:
            print("🛑 Mock gestoppt")
        
        return {'status': 'stopped'}
    
    def emergency_stop(self):
        """Notaus - Sofortiger Stopp"""
        self.emergency_stopped = True
        self.stop()
        
        print("🚨 MOTOR NOT-STOPP AKTIVIERT!")
        
        # Nach 2 Sekunden Reset erlauben
        def reset_emergency():
            time.sleep(2.0)
            self.emergency_stopped = False
            print("✅ Motor-Notaus zurückgesetzt")
        
        threading.Thread(target=reset_emergency, daemon=True).start()
        
        return {'status': 'emergency_stop_activated'}
    
    def get_status(self):
        """Motor-Status abrufen"""
        return {
            'is_moving': self.is_moving,
            'direction': self.current_direction,
            'speed': self.current_speed,
            'emergency_stopped': self.emergency_stopped,
            'hardware_available': self.gpio_available,
            'timestamp': int(time.time())
        }
    
    def set_motor_calibration(self, left_factor=1.0, right_factor=1.0):
        """Motor-Kalibrierung für Geradeausfahrt"""
        self.left_motor_factor = left_factor
        self.right_motor_factor = right_factor
        print(f"⚙️ Motor-Kalibrierung: Links={left_factor}, Rechts={right_factor}")
    
    def cleanup(self):
        """GPIO aufräumen"""
        if self.gpio_available:
            try:
                import RPi.GPIO as GPIO
                
                # PWM stoppen
                for motor in self.motor_pins:
                    pwm = getattr(self, f'{motor}_pwm', None)
                    if pwm:
                        pwm.stop()
                
                GPIO.cleanup()
                print("🧹 Motor-GPIO aufgeräumt")
            except:
                pass

# Globale Instanz
motor_controller = MotorController()

# Cleanup bei Programmende
import atexit
atexit.register(motor_controller.cleanup)