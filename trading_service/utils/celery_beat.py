from celery.schedules import crontab
from trading_service.utils.celery_config import celery

celery.conf.beat_schedule = {
    "refresh_monthly_views": {
        "task": "trading_service.tasks.reporting_tasks.refresh_materialized_views",
        "schedule": crontab(minute=0, hour=0, day_of_month=1),  # Runs 1st day of each month
    }
}
