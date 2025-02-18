import pytest
from app.server import create_app
from app.database import db
from sqlalchemy import text
import os

@pytest.fixture(scope="session")
def test_app():
    """Create a Flask app configured for testing"""
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "TEST_DATABASE_URL", "postgresql://postgres:postgres@localhost:5433/test_trading_db"
    )  # Use a separate test DB
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    return app

@pytest.fixture(scope="function")
def test_client(test_app):
    """Set up test database and Flask test client"""
    with test_app.app_context():

        db.create_all()
        db.session.commit()

        client = test_app.test_client()
        yield client

        db.session.rollback()
        db.session.remove()
