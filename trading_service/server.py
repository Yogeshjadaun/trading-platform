from flask import Flask
from dotenv import load_dotenv
import os
from trading_service.database import init_db
from trading_service.routes.traders import traders_bp
from trading_service.routes.inventory import inventory_bp
from trading_service.routes.trades import trades_bp
from trading_service.utils.cache import init_cache
from trading_service.utils.celery_config import celery
from trading_service.routes.reporting import reporting_bp
from trading_service.routes.health import health_bp

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
