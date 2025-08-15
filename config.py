"""
Configuration file for Ozark Finances Flask Application
"""

import os
from pathlib import Path

class Config:
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = True  # Set to False in production
    
    # Database settings
    DATABASE_PATH = os.environ.get('DATABASE_PATH') or os.path.abspath('ozark_finances.db')
    DATA_DIR = Path(os.environ.get('DATA_DIR') or os.path.dirname(os.path.abspath('ozark_finances.db')))
    
    # Application settings
    HOST = '0.0.0.0'
    PORT = 5000
    
    # File upload settings - use local directories
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = 'uploads'  # Local uploads folder
    GENERATED_FOLDER = 'generated'  # Local generated folder
    ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}
    
    # Excel scanning settings
    EXCEL_INVOICE_CELLS = {
        'invoice_id': 'C13',
        'date': 'C14', 
        'excl': 'F43',
        'btw': 'F44',
        'incl': 'F45'
    }
    
    # Paths (adjust these to match your AutoHotkey setup)
    FACTUREN_PATH = os.environ.get('FACTUREN_PATH') or 'G:/My Drive/Bakker Services/Facturen'
    ADMINISTRATIE_PATH = os.environ.get('ADMINISTRATIE_PATH') or 'G:/My Drive/Bakker Services/Administratie'
    
    @staticmethod
    def init_app(app):
        """Initialize application with this config"""
        # Ensure upload folders exist
        import os
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.GENERATED_FOLDER, exist_ok=True)

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'production-secret-key-must-be-set'

class TestingConfig(Config):
    TESTING = True
    DATABASE_PATH = ':memory:'  # In-memory database for testing

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
