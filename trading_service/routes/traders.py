from flask import Blueprint, jsonify, request
from trading_service.models import Trader
from trading_service.database import db
from trading_service.utils.cache import cache

traders_bp = Blueprint('traders', __name__)

@traders_bp.route('', methods=['POST'])
def create_trader():
    """Create a new trader and invalidate cache"""
    data = request.json
    trader = Trader(name=data['name'], trader_type=data['trader_type'])
    db.session.add(trader)
    db.session.commit()

    cache.delete('all_traders')
    return jsonify({"message": "Trader created", "trader_id": trader.id}), 201

@traders_bp.route('', methods=['GET'])
@cache.cached(timeout=300, key_prefix="all_traders")
def get_traders():
    """Retrieve all traders (cached)"""
    traders = Trader.query.all()
    return jsonify([{"id": t.id, "name": t.name, "trader_type": t.trader_type} for t in traders])

@traders_bp.route('/<int:trader_id>', methods=['GET'])
@cache.cached(timeout=300, key_prefix=lambda: f"trader_{trader_id}")
def get_trader(trader_id):
    """Retrieve a single trader by ID (cached)"""
    trader = Trader.query.get(trader_id)
    if not trader:
        return jsonify({"error": "Trader not found"}), 404
    return jsonify({"id": trader.id, "name": trader.name, "trader_type": trader.trader_type})

@traders_bp.route('/<int:trader_id>', methods=['PUT'])
def update_trader(trader_id):
    """Update a trader and invalidate cache"""
    trader = Trader.query.get(trader_id)
    if not trader:
        return jsonify({"error": "Trader not found"}), 404

    data = request.json
    trader.name = data.get("name", trader.name)
    trader.trader_type = data.get("trader_type", trader.trader_type)

    db.session.commit()

    cache.delete('all_traders')
    cache.delete(f"trader_{trader_id}")
    return jsonify({"message": "Trader updated", "trader_id": trader.id})

@traders_bp.route('/<int:trader_id>', methods=['DELETE'])
def delete_trader(trader_id):
    """Delete a trader and invalidate cache"""
    trader = Trader.query.get(trader_id)
    if not trader:
        return jsonify({"error": "Trader not found"}), 404

    db.session.delete(trader)
    db.session.commit()

    cache.delete('all_traders')
    cache.delete(f"trader_{trader_id}")
    return jsonify({"message": "Trader deleted"})
