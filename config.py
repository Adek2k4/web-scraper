import os

class Config:
    """konfiguracja aplikacji"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # url-e modulow (beda w docker containers)
    ENGINE_API_URL = os.environ.get('ENGINE_API_URL') or 'http://localhost:5001'
    DATABASE_API_URL = os.environ.get('DATABASE_API_URL') or 'http://localhost:5002'
    
    # flask config
    DEBUG = os.environ.get('FLASK_ENV') == 'development'
