from datetime import datetime
from trading_service.database import db
from trading_service.models.trade_models import Trade, TradeCommodity, TradeStatus, ReverseTrade
from trading_service.models.trader_models import Trader
from trading_service.utils.helpers import  log_trade_action
from trading_service.utils.validators import has_sufficient_inventory
from trading_service.utils.constants import *


def create_trade(trader_from, trader_to, offered_items, requested_items):
    """Creates a trade request after necessary validations"""

    sender = Trader.query.get(trader_from)
    recipient = Trader.query.get(trader_to)
    if not sender or not recipient:
        return {"error": ERROR_INVALID_TRADERS}, 400

    if not has_sufficient_inventory(trader_from, offered_items):
        return {"error": ERROR_SENDER_INSUFFICIENT}, 400

    if not has_sufficient_inventory(trader_to, requested_items):
        return {"error": ERROR_RECIPIENT_INSUFFICIENT}, 400

    trade = Trade(
        traded_from=trader_from,
        traded_to=trader_to,
        status=TradeStatus.PENDING.value,
        created_at=datetime.utcnow()
    )
    db.session.add(trade)
    db.session.commit()

    for item in offered_items:
        db.session.add(TradeCommodity(trade_id=trade.id, commodity_id=item["commodity_id"], quantity=item["quantity"],
                                      role="offer"))

    for item in requested_items:
        db.session.add(TradeCommodity(trade_id=trade.id, commodity_id=item["commodity_id"], quantity=item["quantity"],
                                      role="request"))

    db.session.commit()
    log_trade_action(trade.id, "Trade Created", f"Trade initiated by trader {trader_from}", trader_from)

    return {"message": SUCCESS_TRADE_CREATED, "trade_id": trade.id}, 201


def respond_trade(trade_id, response):
    """Handles trade acceptance or rejection"""

    trade = Trade.query.get(trade_id)
    if not trade:
        return {"error": ERROR_TRADE_NOT_FOUND}, 404

    if trade.status != TradeStatus.PENDING.value:
        return {"error": ERROR_TRADE_NOT_PENDING}, 400

    if response == "reject":
        trade.status = TradeStatus.REJECTED.value
        db.session.commit()
        log_trade_action(trade.id, "Trade Rejected", SUCCESS_TRADE_REJECTED, trade.traded_to)
        return {"message": SUCCESS_TRADE_REJECTED}, 200

    offered_items = TradeCommodity.query.filter_by(trade_id=trade.id, role="offer").all()
    requested_items = TradeCommodity.query.filter_by(trade_id=trade.id, role="request").all()

    if not has_sufficient_inventory(trade.traded_from,
                                    [{"commodity_id": item.commodity_id, "quantity": item.quantity} for item in
                                     offered_items]):
        trade.status = TradeStatus.REJECTED.value
        db.session.commit()
        return {"error": ERROR_SENDER_INSUFFICIENT}, 400

    if not has_sufficient_inventory(trade.traded_to,
                                    [{"commodity_id": item.commodity_id, "quantity": item.quantity} for item in
                                     requested_items]):
        trade.status = TradeStatus.REJECTED.value
        db.session.commit()
        return {"error": ERROR_RECIPIENT_INSUFFICIENT}, 400

    trade.status = TradeStatus.ACCEPTED.value
    db.session.commit()
    log_trade_action(trade.id, "Trade Accepted", SUCCESS_TRADE_ACCEPTED, trade.traded_to)

    return {"message": SUCCESS_TRADE_ACCEPTED}, 200


def reverse_trade(trade_id, reason, trade_reversed_by):
    """Handles trade reversal"""
    trade = Trade.query.get(trade_id)
    if not trade or trade.status != TradeStatus.ACCEPTED.value:
        return {"error": ERROR_TRADE_NOT_FOUND}, 400

    existing_reversal = ReverseTrade.query.filter_by(original_trade_id=trade_id).first()
    if existing_reversal:
        return {"error": ERROR_ALREADY_REVERSED}, 400

    reverse_trade = ReverseTrade(original_trade_id=trade_id, reverse_reason=reason, trade_reversed_by=trade_reversed_by)
    db.session.add(reverse_trade)
    trade.status = TradeStatus.REVERSED.value
    db.session.commit()
    log_trade_action(trade.id, "Trade Reversed", f"Trade reversed: {reason}", trade.traded_to)

    return {"message": SUCCESS_TRADE_REVERSED}, 200
