import pytest
from app.server import create_app
from app.database import db

@pytest.fixture(scope="function")
def test_client():
    """Fixture to create a test Flask application and client"""
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    with app.app_context():
        db.create_all()
        client = app.test_client()
        yield client
        db.session.rollback()
        db.session.remove()
        db.drop_all()
