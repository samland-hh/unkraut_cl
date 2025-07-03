# arm_debug.py - Debug für Roboterarm Joint-Move Fehler
import requests
import json

def test_arm_joint_debug():
    """Debugge den spezifischen Arm-Joint-Fehler"""
    print("🦾 Roboterarm Joint-Move Debug")
    print("==============================")
    
    url = "http://localhost:5000/api/arm/move/joint"
    data = {"joint": "base", "angle": 90}
    
    print(f"🔍 Teste: POST {url}")
    print(f"📦 Data: {data}")
    
    try:
        response = requests.post(url, json=data, timeout=5)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Headers: {dict(response.headers)}")
        print(f"📄 Response Content:")
        
        if response.headers.get('content-type', '').startswith('application/json'):
            try:
                json_response = response.json()
                print(json.dumps(json_response, indent=2))
            except:
                print("(JSON parsing failed)")
                print(response.text)
        else:
            print(response.text)
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

def test_arm_direct():
    """Teste Roboterarm direkt"""
    print("\n🔧 Teste Roboterarm direkt:")
    
    try:
        from hardware.robot_arm import robot_arm
        
        print("✅ Roboterarm importiert")
        
        # Teste get_arm_info (das funktioniert)
        info = robot_arm.get_arm_info()
        print(f"📊 Arm Info: Hardware={info['controller']['hardware_available']}")
        
        # Teste move_joint direkt
        print("🎯 Teste move_joint direkt...")
        success = robot_arm.move_joint('base', 90.0)
        print(f"📊 move_joint Ergebnis: {success}")
        
        # Teste mit verschiedenen Joints
        joints = ['base', 'shoulder', 'elbow', 'wrist', 'gripper', 'tool']
        for joint in joints:
            try:
                result = robot_arm.move_joint(joint, 90.0)
                print(f"  ✅ {joint}: {result}")
            except Exception as e:
                print(f"  ❌ {joint}: {e}")
                
    except Exception as e:
        print(f"❌ Roboterarm-Test fehlgeschlagen: {e}")
        import traceback
        traceback.print_exc()

def test_pca9685_direct():
    """Teste PCA9685 direkt"""
    print("\n🔌 Teste PCA9685 direkt:")
    
    try:
        from adafruit_pca9685 import PCA9685
        import board
        import busio
        
        print("✅ PCA9685 Library verfügbar")
        
        # Teste I2C Verbindung
        i2c = busio.I2C(board.SCL, board.SDA)
        pca = PCA9685(i2c, address=0x40)
        pca.frequency = 50
        
        print("✅ PCA9685 Hardware verbunden")
        
        # Teste einen Servo direkt
        # 90° entspricht ca. 1500µs Pulslänge
        pulse_length = int(500 + (90 / 180.0) * 2000)  # 1500µs
        duty_cycle = int(pulse_length * 65535 / 20000)  # 20ms Periode
        
        pca.channels[0].duty_cycle = duty_cycle
        print(f"✅ Servo 0 auf 90° gesetzt (duty_cycle: {duty_cycle})")
        
        pca.deinit()
        
    except ImportError:
        print("❌ adafruit_pca9685 Library fehlt")
        print("💡 Install: pip install adafruit-circuitpython-pca9685")
    except Exception as e:
        print(f"❌ PCA9685-Test fehlgeschlagen: {e}")
        import traceback
        traceback.print_exc()

def test_api_route_direct():
    """Teste API-Route direkt"""
    print("\n🔌 Teste API-Route direkt:")
    
    try:
        from app.routes.api_routes import move_arm_joint
        from flask import Flask, request
        
        # Simuliere Flask Request
        app = Flask(__name__)
        with app.test_request_context(json={'joint': 'base', 'angle': 90}):
            response = move_arm_joint()
            print(f"📊 API Response: {response}")
            
    except Exception as e:
        print(f"❌ API-Route-Test fehlgeschlagen: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_arm_joint_debug()
    test_arm_direct() 
    test_pca9685_direct()
    test_api_route_direct()
    
    print("\n💡 Lösungsvorschläge:")
    print("===================")
    print("1. GPIO-Konflikt: sudo systemctl stop pigpio")
    print("2. I2C-Problem: sudo i2cdetect -y 1")
    print("3. Permission: sudo usermod -a -G gpio,i2c $USER")
    print("4. PCA9685 Reset: GPIO-Pin kurz auf LOW")
    print("5. Library Update: pip install --upgrade adafruit-circuitpython-pca9685")