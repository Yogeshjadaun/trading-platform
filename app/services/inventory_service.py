from app.database import db
from app.models.inventory_models import Commodity, CommodityProperty, TraderInventory
from app.utils.constants import *
from app.utils.helpers import commit_and_flush

def create_commodity(name, category, properties=[]):
    """Creates a commodity with optional properties"""
    if not name or not category:
        return {"error": ERROR_MISSING_COMMODITY_DATA}, 400

    commodity = Commodity(name=name, category=category)
    db.session.add(commodity)
    db.session.flush()

    created_properties = []
    for prop in properties:
        if "property_name" in prop and "property_value" in prop:
            property_entry = CommodityProperty(
                commodity_id=commodity.id,
                property_name=prop["property_name"],
                property_value=prop["property_value"]
            )
            db.session.add(property_entry)
            created_properties.append({
                "property_id": property_entry.id,
                "property_name": prop["property_name"],
                "property_value": prop["property_value"]
            })

    commit_and_flush()

    return {
        "message": SUCCESS_COMMODITY_CREATED,
        "commodity": {
            "id": commodity.id,
            "name": commodity.name,
            "category": commodity.category,
            "properties": created_properties
        }
    }, 201


def get_all_commodities():
    """Retrieve all commodities"""
    commodities = Commodity.query.all()
    return [{"id": c.id, "name": c.name, "category": c.category} for c in commodities], 200


def get_commodity_by_id(commodity_id):
    """Retrieve a single commodity"""
    commodity = Commodity.query.get(commodity_id)
    if not commodity:
        return {"error": ERROR_COMMODITY_NOT_FOUND}, 404
    return {"id": commodity.id, "name": commodity.name, "category": commodity.category}, 200


def update_commodity(commodity_id, name, category):
    """Update commodity"""
    commodity = Commodity.query.get(commodity_id)
    if not commodity:
        return {"error": ERROR_COMMODITY_NOT_FOUND}, 404

    commodity.name = name or commodity.name
    commodity.category = category or commodity.category
    commit_and_flush()
    return {"message": SUCCESS_COMMODITY_UPDATED, "commodity_id": commodity.id}, 200


def delete_commodity(commodity_id):
    """Delete commodity"""
    commodity = Commodity.query.get(commodity_id)
    if not commodity:
        return {"error": ERROR_COMMODITY_NOT_FOUND}, 404

    db.session.delete(commodity)
    commit_and_flush()
    return {"message": SUCCESS_COMMODITY_DELETED}, 200


def create_property(commodity_id, property_name, property_value):
    """Create a property"""
    commodity = Commodity.query.get(commodity_id)
    if not commodity:
        return {"error": ERROR_COMMODITY_NOT_FOUND}, 404

    property_entry = CommodityProperty(
        commodity_id=commodity_id,
        property_name=property_name,
        property_value=property_value
    )
    db.session.add(property_entry)
    commit_and_flush()
    return {"message": SUCCESS_PROPERTY_CREATED, "property_id": property_entry.id}, 201


def get_properties(commodity_id):
    """Retrieve all properties for a commodity"""
    commodity = Commodity.query.get(commodity_id)
    if not commodity:
        return {"error": ERROR_COMMODITY_NOT_FOUND}, 404

    properties = CommodityProperty.query.filter_by(commodity_id=commodity_id).all()
    return [{"id": p.id, "property_name": p.property_name, "property_value": p.property_value} for p in properties], 200

def get_property(property_id):
    """Retrieve a single property"""
    property_entry = CommodityProperty.query.get(property_id)
    if not property_entry:
        return {"error": ERROR_PROPERTY_NOT_FOUND}, 404

    return {"id": property_entry.id, "property_name": property_entry.property_name, "property_value": property_entry.property_value}, 200


def update_property(property_id, property_name, property_value):
    """Update a property"""
    property_entry = CommodityProperty.query.get(property_id)
    if not property_entry:
        return {"error": ERROR_PROPERTY_NOT_FOUND}, 404

    property_entry.property_name = property_name or property_entry.property_name
    property_entry.property_value = property_value or property_entry.property_value
    commit_and_flush()
    return {"message": SUCCESS_PROPERTY_UPDATED, "property_id": property_entry.id}, 200


def delete_property(property_id):
    """Delete a property"""
    property_entry = CommodityProperty.query.get(property_id)
    if not property_entry:
        return {"error": ERROR_PROPERTY_NOT_FOUND}, 404

    db.session.delete(property_entry)
    commit_and_flush()
    return {"message": SUCCESS_PROPERTY_DELETED}, 200


def add_inventory(trader_id, commodity_id, quantity):
    """Add inventory"""
    inventory = TraderInventory(trader_id=trader_id, commodity_id=commodity_id, quantity=quantity)
    db.session.add(inventory)
    commit_and_flush()
    return {"message": SUCCESS_INVENTORY_UPDATED}, 201


def get_inventory(trader_id):
    """Retrieve inventory"""
    inventory = TraderInventory.query.filter_by(trader_id=trader_id).all()
    return [{"commodity_id": item.commodity_id, "quantity": item.quantity} for item in inventory], 200


def delete_inventory(trader_id, commodity_id):
    """Delete inventory entry"""
    inventory = TraderInventory.query.filter_by(trader_id=trader_id, commodity_id=commodity_id).first()
    if not inventory:
        return {"error": ERROR_INVENTORY_NOT_FOUND}, 404

    db.session.delete(inventory)
    commit_and_flush()
    return {"message": SUCCESS_INVENTORY_DELETED}, 200
