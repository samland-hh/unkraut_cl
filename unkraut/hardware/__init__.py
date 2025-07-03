# hardware/__init__.py
"""
Hardware-Module für Unkraut-2025
"""

from .camera import camera_manager
from .robot_arm import robot_arm
from .motors import motor_controller
from .sensors import sensor_manager, get_sensor_data, get_system_stats

__version__ = "1.0.0"
__all__ = [
    'camera_manager',
    'robot_arm', 
    'motor_controller',
    'sensor_manager',
    'get_sensor_data',
    'get_system_stats'
]