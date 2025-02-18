from flask import Blueprint, jsonify, request
from trading_service.services.trade_service import create_trade, respond_trade, reverse_trade
from trading_service.utils.cache import cache

trades_bp = Blueprint('trades', __name__)

@trades_bp.route('/trade', methods=['POST'])
def trade():
    """Create a new trade request"""
    data = request.json
    response, status = create_trade(
        data.get("traded_from"),
        data.get("traded_to"),
        data.get("offered_items"),
        data.get("requested_items")
    )

    cache.delete(f"trades_{data.get('traded_from')}")
    cache.delete(f"trades_{data.get('traded_to')}")
    return jsonify(response), status


@trades_bp.route('/trade/<int:trade_id>/response', methods=['POST'])
def handle_trade_response(trade_id):
    """Accept or reject a trade"""
    data = request.json
    response, status = respond_trade(trade_id, data.get("response"))

    cache.delete(f"trade_{trade_id}")
    return jsonify(response), status


@trades_bp.route('/trade/<int:trade_id>/reverse', methods=['POST'])
def handle_trade_reversal(trade_id):
    """Reverse a trade"""
    data = request.json
    response, status = reverse_trade(trade_id, data.get("reason"), data.get("trade_reversed_by"))

    cache.delete(f"trade_{trade_id}")
    return jsonify(response), status
