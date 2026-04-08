from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    db.init_app(app)
    from main import main_bp
    app.register_blueprint(main_bp)
    from auth import auth_bp
    app.register_blueprint(auth_bp)
    print(app.url_map)
    return app