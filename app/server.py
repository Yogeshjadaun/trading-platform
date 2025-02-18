from flask import Flask
from dotenv import load_dotenv
import os
from app.database import init_db
from app.routes.traders import traders_bp
from app.routes.inventory import inventory_bp
from app.routes.trades import trades_bp
from app.utils.cache import init_cache
from app.utils.celery_config import celery
from app.routes.reporting import reporting_bp
from app.routes.health import health_bp

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    init_db(app)
    init_cache(app)
    celery.conf.update(app.config)

    app.register_blueprint(health_bp, url_prefix='/health')
    app.register_blueprint(traders_bp, url_prefix='/traders')
    app.register_blueprint(inventory_bp, url_prefix='/inventory')
    app.register_blueprint(trades_bp, url_prefix='/trades')
    app.register_blueprint(reporting_bp, url_prefix='/reports')

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
