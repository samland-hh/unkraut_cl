"""
Hauptkonfiguration für Unkraut-2025
"""
import os

class Config:
    SECRET_KEY = 'unkraut-2025-development-key'
    
    # Pfade
    DATA_DIR = 'data'
    IMAGE_DIR = 'data/images'
    VIDEO_DIR = 'data/videos'  
    LOG_DIR = 'logs'
    BACKUP_DIR = 'backups'
    
    # Hardware
    MOCK_HARDWARE = True

config = Config()
