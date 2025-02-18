from trading_service.utils.celery_config import celery
from trading_service.database import db
from sqlalchemy import text
import logging


def refresh_materialized_views_data():
    """Refresh materialized views for reporting."""
    queries = [
        "REFRESH MATERIALIZED VIEW trade_acceptance_rate;",
        "REFRESH MATERIALIZED VIEW market_conversion_rates;"
    ]

    try:
        with db.engine.connect() as conn:
            for query in queries:
                conn.execute(text(query))  # Execute refresh
            conn.commit()  # Commit transaction
            logging.info("Materialized Views Refreshed Successfully!")
    except Exception as e:
        logging.error(f"Failed to refresh materialized views: {e}")
    finally:
        db.session.remove()  # Ensure session cleanup

@celery.task
def refresh_materialized_views():
    """Refresh materialized views for reporting."""
    refresh_materialized_views_data()