import pytest
import os
import psycopg2
from trading_service.server import create_app
from trading_service.database import db, init_db
from flask_migrate import upgrade

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
TEST_DB_NAME = os.getenv("TEST_DB_NAME", "test_trading_db")

TEST_DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{TEST_DB_NAME}"
ADMIN_DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/postgres"  # Used for DB creation & deletion


def force_disconnect_users(database_name):
    """Force disconnect all active connections to the database."""
    try:
        conn = psycopg2.connect(ADMIN_DB_URL)
        conn.set_session(autocommit=True)
        with conn.cursor() as cur:
            cur.execute(f"""
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = '{database_name}'
                AND pid <> pg_backend_pid();
            """)
        conn.close()
    except Exception as e:
        raise

@pytest.fixture(scope="session")
def create_test_database():
    """Drop and create a fresh test database before running tests."""
    try:
        conn = psycopg2.connect(ADMIN_DB_URL)
        conn.set_session(autocommit=True)  # Enable AUTOCOMMIT to run DROP DATABASE

        with conn.cursor() as cur:
            cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{TEST_DB_NAME}';")
            db_exists = cur.fetchone()

            if db_exists:
                force_disconnect_users(TEST_DB_NAME)  # Ensure no active connections
                cur.execute(f"DROP DATABASE {TEST_DB_NAME};")

            cur.execute(f"CREATE DATABASE {TEST_DB_NAME};")

        conn.close()

    except Exception as e:
        raise


@pytest.fixture(scope="session")
def test_app(create_test_database):
    """Create a new Flask app with a test database and apply migrations."""
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = TEST_DB_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    with app.app_context():
        init_db(app)
        upgrade()  # Apply all migrations
    return app


@pytest.fixture(scope="function")
def test_client(test_app):
    """Set up a test client with a fresh database session per test."""
    with test_app.app_context():
        connection = db.engine.connect()
        transaction = connection.begin()
        db.session.begin_nested()  # Use nested transactions for rollback

        client = test_app.test_client()
        yield client  # Run the test

        db.session.rollback()  # Rollback changes
        transaction.rollback()
        connection.close()


@pytest.fixture(scope="session", autouse=True)
def drop_test_database(request):
    """Drop the test database after all tests have run."""
    def cleanup():
        try:
            conn = psycopg2.connect(ADMIN_DB_URL)
            conn.set_session(autocommit=True)

            with conn.cursor() as cur:
                cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{TEST_DB_NAME}';")
                db_exists = cur.fetchone()

                if db_exists:
                    force_disconnect_users(TEST_DB_NAME)  # Ensure no active connections
                    cur.execute(f"DROP DATABASE {TEST_DB_NAME};")
            conn.close()

        except Exception as e:
            raise

    request.addfinalizer(cleanup)  # Ensure the cleanup runs at the end of testing
