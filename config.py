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
    
    # Discord Logging Configuration
    DISCORD_LOGGING_ENABLED = os.environ.get('DISCORD_LOGGING_ENABLED', 'True').lower() == 'true'
    DISCORD_RATE_LIMIT = int(os.environ.get('DISCORD_RATE_LIMIT', '10'))  # messages per minute
    
    # Discord Webhook URLs (use environment variables for security)
    DISCORD_WEBHOOKS = {
        'finance': os.environ.get('DISCORD_WEBHOOK_FINANCE', 'https://discord.com/api/webhooks/1411770837710802964/4-D4P9ljIskDIbM_g69b1xABtEv6GSrYcR2njYevGReMvLAUpfPmYmRQOBcCrnRsLLEp'),
        'system': os.environ.get('DISCORD_WEBHOOK_SYSTEM', 'https://discord.com/api/webhooks/1411771095245390036/wPndYq9E6ZXMEiFV2BVyA0tdzqJ9Oem9sSavOuJjKSNggfd5g6KO6eEwduBP8VJLGlLK'),
        'errors': os.environ.get('DISCORD_WEBHOOK_ERRORS', 'https://discord.com/api/webhooks/1411771235422965920/vtLynm4o2FHRCMK8lFn5uP6TevDo4utSx74gc4usnbWX6QHacJIkVK24PD-KAXdglTub'),
        'activity': os.environ.get('DISCORD_WEBHOOK_ACTIVITY', 'https://discord.com/api/webhooks/1411771395204972604/Ovu44-8_unmKI6eHlb_qd9SXJtQBgLAfQ1Me2BTbaMy9IiiM4DFvQBFbI9hN9S_SWkM-')
    }
    
    # Discord Logging Feature Toggles
    DISCORD_LOG_FEATURES = {
        'finance_events': os.environ.get('DISCORD_LOG_FINANCE', 'True').lower() == 'true',
        'system_events': os.environ.get('DISCORD_LOG_SYSTEM', 'True').lower() == 'true',
        'error_events': os.environ.get('DISCORD_LOG_ERRORS', 'True').lower() == 'true',
        'user_activity': os.environ.get('DISCORD_LOG_ACTIVITY', 'True').lower() == 'true',
        'performance_warnings': os.environ.get('DISCORD_LOG_PERFORMANCE', 'True').lower() == 'true',
        'daily_summaries': os.environ.get('DISCORD_LOG_SUMMARIES', 'True').lower() == 'true'
    }
    
    # Discord Retry and Reliability Settings
    DISCORD_RETRY_ATTEMPTS = int(os.environ.get('DISCORD_RETRY_ATTEMPTS', '3'))
    DISCORD_RETRY_DELAY = float(os.environ.get('DISCORD_RETRY_DELAY', '1.0'))  # seconds
    DISCORD_TIMEOUT = int(os.environ.get('DISCORD_TIMEOUT', '10'))  # seconds
    DISCORD_QUEUE_SIZE = int(os.environ.get('DISCORD_QUEUE_SIZE', '100'))  # max queued messages
    
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
