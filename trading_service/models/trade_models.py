from enum import Enum

from sqlalchemy.dialects.postgresql import ENUM

from trading_service.database import db
from datetime import datetime

TradeStatusEnum = ENUM("pending", "accepted", "rejected", "reversed", name="tradestatus", create_type=False)

class TradeStatus(Enum):
    DRAFT = "draft"
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    REVERSED = "reversed"

class Trade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    traded_from = db.Column(db.Integer, db.ForeignKey('trader.id'))
    traded_to = db.Column(db.Integer, db.ForeignKey('trader.id'))
    status = db.Column(TradeStatusEnum, default="pending", nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class TradeCommodity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trade_id = db.Column(db.Integer, db.ForeignKey('trade.id'))
    commodity_id = db.Column(db.Integer, db.ForeignKey('commodity.id'))
    quantity = db.Column(db.Integer, nullable=False)
    role = db.Column(db.String(10), nullable=False)

class ReverseTrade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_trade_id = db.Column(db.Integer, db.ForeignKey('trade.id'))
    reverse_reason = db.Column(db.Text, nullable=False)
    trade_reversed_by = db.Column(db.Integer, db.ForeignKey('trader.id'))
    penalty = db.Column(db.Float, default=0.0)
    reversed_at = db.Column(db.DateTime, default=datetime.utcnow)

class TradeRule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rule_name = db.Column(db.String(100), nullable=False)
    trader_id = db.Column(db.Integer, db.ForeignKey('trader.id'), nullable=True)
    condition = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
