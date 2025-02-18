from flask import Blueprint, jsonify
from sqlalchemy import text

from app.database import db
from redis import Redis
from celery.result import AsyncResult
from app.utils.celery_config import celery
import os

health_bp = Blueprint("health", __name__)

# 🔹 Redis Connection
redis_client = Redis(host=os.getenv("REDIS_HOST", "localhost"), port=6379, db=0, socket_connect_timeout=1)

@health_bp.route("", methods=["GET"])
def health_check():
    """Health check API for Flask, Database, Redis, and Celery"""
    health_status = {
        "flask": "running",
        "database": "unknown",
        "redis": "unknown",
        "celery": "unknown"
    }

    try:
        db.session.execute(text("SELECT 1"))  # Simple query to test DB connection
        health_status["database"] = "connected"
    except Exception as e:
        health_status["database"] = f"error: {str(e)}"

    try:
        if redis_client.ping():
            health_status["redis"] = "connected"
    except Exception as e:
        health_status["redis"] = f"error: {str(e)}"

    try:
        test_task = celery.send_task("app.tasks.ping_task")
        result = AsyncResult(test_task.id, app=celery)
        if result:
            health_status["celery"] = "connected"
    except Exception as e:
        health_status["celery"] = f"error: {str(e)}"

    return jsonify(health_status), 200 if all(status == "connected" for status in health_status.values()) else 500
