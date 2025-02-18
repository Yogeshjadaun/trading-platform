from app.database import db
from datetime import datetime

class TradeAuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trade_id = db.Column(db.Integer, db.ForeignKey('trade.id'))
    event_type = db.Column(db.String(50), nullable=False)
    event_details = db.Column(db.Text)
    triggered_by = db.Column(db.Integer, db.ForeignKey('trader.id'))
    event_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
