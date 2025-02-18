from datetime import datetime
from app.database import db
from app.models.audit_models import TradeAuditLog

def log_trade_action(trade_id, event_type, details, triggered_by):
    """Logs trade events into the audit table"""
    audit_entry = TradeAuditLog(
        trade_id=trade_id,
        event_type=event_type,
        event_details=details,
        triggered_by=triggered_by,
        event_timestamp=datetime.utcnow()
    )
    db.session.add(audit_entry)
    db.session.commit()

def commit_and_flush():
    """Commit transaction and handle any database errors."""
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e
