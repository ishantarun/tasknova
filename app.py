import os
from flask import Flask
from config import Config
from database import close_db, init_db
from routes.main import main_bp
from routes.api import api_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Register database teardown
    app.teardown_appcontext(close_db)

    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)

    # Initialize database tables and initial seed data
    init_db(app)

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"==================================================")
    print(f"  TaskNova — Your Day, Under Control")
    print(f"  Running locally on http://127.0.0.1:{port}")
    print(f"==================================================")
    app.run(host='127.0.0.1', port=port, debug=True)
