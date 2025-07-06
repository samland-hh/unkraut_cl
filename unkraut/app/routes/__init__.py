# app/routes/__init__.py
"""
Routes Package für Unkraut-2025
"""

from . import main_routes, control_routes, arm_routes, camera_routes, ai_routes, api_routes, combined_routes, debug_routes

__all__ = [
    'main_routes',
    'control_routes', 
    'arm_routes',
    'camera_routes',
    'ai_routes',
    'api_routes',
    'combined_routes',
    'debug_routes'
]