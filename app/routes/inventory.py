from flask import Blueprint, jsonify, request
from app.services.inventory_service import *
from app.utils.cache import cache

inventory_bp = Blueprint('inventory', __name__)

@inventory_bp.route('/commodities/full', methods=['POST'])
def create_commodity_with_properties():
    """Create a commodity along with its properties"""
    data = request.json
    response, status = create_commodity(data.get("name"), data.get("category"), data.get("properties", []))

    cache.delete("all_commodities")
    return jsonify(response), status


@inventory_bp.route('/commodities', methods=['POST'])
def create_commodity_route():
    """Create a new commodity"""
    data = request.json
    response, status = create_commodity(data.get("name"), data.get("category"))
    cache.delete("all_commodities")

    return jsonify(response), status


@inventory_bp.route('/commodities', methods=['GET'])
@cache.cached(timeout=300, key_prefix="all_commodities")
def get_commodities_route():
    """Retrieve all commodities (cached)"""
    response, status = get_all_commodities()
    return jsonify(response), status


@inventory_bp.route('/commodities/<int:commodity_id>', methods=['GET'])
@cache.cached(timeout=300, key_prefix=lambda: f"commodity_{request.view_args.get('commodity_id')}")
def get_commodity_route(commodity_id):
    """Retrieve a single commodity by ID (cached)"""
    response, status = get_commodity_by_id(commodity_id)
    return jsonify(response), status


@inventory_bp.route('/commodities/<int:commodity_id>', methods=['PUT'])
def update_commodity_route(commodity_id):
    """Update a commodity"""
    data = request.json
    response, status = update_commodity(commodity_id, data.get("name"), data.get("category"))

    cache.delete("all_commodities")
    cache.delete(f"commodity_{commodity_id}")
    return jsonify(response), status


@inventory_bp.route('/commodities/<int:commodity_id>', methods=['DELETE'])
def delete_commodity_route(commodity_id):
    """Delete a commodity"""
    response, status = delete_commodity(commodity_id)

    cache.delete("all_commodities")
    cache.delete(f"commodity_{commodity_id}")
    return jsonify(response), status


@inventory_bp.route('/commodities/<int:commodity_id>/properties', methods=['POST'])
def create_property_route(commodity_id):
    """Create a property for a commodity"""
    data = request.json
    response, status = create_property(commodity_id, data.get("property_name"), data.get("property_value"))

    cache.delete(f"commodity_{commodity_id}")
    return jsonify(response), status


@inventory_bp.route('/commodities/<int:commodity_id>/properties', methods=['GET'])
@cache.cached(timeout=300, key_prefix=lambda: f"properties_{request.view_args.get('commodity_id')}")
def get_properties_route(commodity_id):
    """Retrieve all properties of a commodity (cached)"""
    response, status = get_properties(commodity_id)
    return jsonify(response), status


@inventory_bp.route('/commodities/properties/<int:property_id>', methods=['GET'])
@cache.cached(timeout=300, key_prefix=lambda: f"property_{request.view_args.get('property_id')}")
def get_property_route(property_id):
    """Retrieve a single property (cached)"""
    response, status = get_property(property_id)
    return jsonify(response), status


@inventory_bp.route('/commodities/properties/<int:property_id>', methods=['PUT'])
def update_property_route(property_id):
    """Update a property"""
    data = request.json
    response, status = update_property(property_id, data.get("property_name"), data.get("property_value"))

    cache.delete(f"property_{property_id}")
    return jsonify(response), status


@inventory_bp.route('/commodities/properties/<int:property_id>', methods=['DELETE'])
def delete_property_route(property_id):
    """Delete a property"""
    response, status = delete_property(property_id)

    cache.delete(f"property_{property_id}")
    return jsonify(response), status


@inventory_bp.route('', methods=['POST'])
def add_inventory_route():
    """Add inventory to a trader"""
    data = request.json
    response, status = add_inventory(data.get("trader_id"), data.get("commodity_id"), data.get("quantity"))

    cache.delete(f"inventory_{data.get('trader_id')}")
    return jsonify(response), status


@inventory_bp.route('/<int:trader_id>', methods=['GET'])
@cache.cached(timeout=300, key_prefix=lambda: f"inventory_{request.view_args.get('trader_id')}")
def get_inventory_route(trader_id):
    """Retrieve inventory for a trader (cached)"""
    response, status = get_inventory(trader_id)
    return jsonify(response), status


@inventory_bp.route('/inventory/<int:trader_id>/<int:commodity_id>', methods=['DELETE'])
def delete_inventory_route(trader_id, commodity_id):
    """Delete an inventory entry"""
    response, status = delete_inventory(trader_id, commodity_id)

    cache.delete(f"inventory_{trader_id}")
    return jsonify(response), status
