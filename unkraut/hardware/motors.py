"""
Motorsteuerung für Unkraut-2025 (Mock-Version)
"""
import time

class MotorController:
    def __init__(self):
        self.is_moving = False
        self.current_speed = 0
        self.current_direction = 'stop'
        print("🚗 Mock-MotorController initialisiert")
    
    def move(self, direction, speed=50, duration=0):
        self.current_direction = direction
        self.current_speed = speed
        print(f"🚀 Mock: Moving {direction} at {speed}%")
        
        if duration > 0:
            time.sleep(duration)
            self.stop()
        
        return {'status': 'success', 'direction': direction, 'speed': speed}
    
    def stop(self):
        self.is_moving = False
        self.current_direction = 'stop'
        print("🛑 Mock: Motors stopped")
        return {'status': 'stopped'}
    
    def emergency_stop(self):
        print("🚨 EMERGENCY STOP")
        return self.stop()
    
    def get_status(self):
        return {
            'is_moving': self.is_moving,
            'direction': self.current_direction,
            'speed': self.current_speed
        }

# Globale Instanz
motor_controller = MotorController()
