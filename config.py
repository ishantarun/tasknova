import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # On Vercel / serverless platforms, only /tmp is writable
    if os.environ.get('VERCEL') or os.environ.get('AWS_LAMBDA_FUNCTION_NAME'):
        DATABASE_PATH = '/tmp/tasknova.db'
    else:
        DATABASE_PATH = os.path.join(BASE_DIR, 'instance', 'tasknova.db')

    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
    TEMPLATES_AUTO_RELOAD = True
