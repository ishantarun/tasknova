import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'tasknova-secure-dev-key-2026-v1')
    DATABASE_PATH = os.path.join(BASE_DIR, 'instance', 'tasknova.db')
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
    TEMPLATES_AUTO_RELOAD = True
