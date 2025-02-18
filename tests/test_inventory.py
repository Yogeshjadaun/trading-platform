import pytest
from trading_service.models.inventory_models import CommodityPropertyType
from trading_service.utils.constants import SUCCESS_COMMODITY_UPDATED, SUCCESS_COMMODITY_DELETED, SUCCESS_PROPERTY_UPDATED, \
    SUCCESS_PROPERTY_DELETED, SUCCESS_INVENTORY_UPDATED


@pytest.fixture(scope="function")
def setup_data(test_client):
    """Set up traders and commodities before running tests"""

    trader_response = test_client.post('/traders', json={"name": "Yogesh", "trader_type": "elf"})
    assert trader_response.status_code == 201
    trader_id = trader_response.json.get("trader_id")

    commodity_1 = test_client.post('/inventory/commodities', json={"name": "Sword", "category": "weapon"})
    commodity_2 = test_client.post('/inventory/commodities', json={"name": "Shield", "category": "defense"})

    assert commodity_1.status_code == 201, f"Commodity 1 creation failed: {commodity_1.json}"
    assert commodity_2.status_code == 201, f"Commodity 2 creation failed: {commodity_2.json}"

    return {
        "trader_id": trader_id,
        "sword_id": commodity_1.json.get("commodity", {}).get("id"),
        "shield_id": commodity_2.json.get("commodity", {}).get("id"),
    }


def test_create_commodity(test_client):
    """Test creating a new commodity"""
    response = test_client.post('/inventory/commodities', json={
        "name": "Helmet",
        "category": "armor"
    })
    assert response.status_code == 201
    assert "commodity" in response.json
    assert "id" in response.json["commodity"]


def test_get_commodities(test_client, setup_data):
    """Test retrieving all commodities"""
    response = test_client.get('/inventory/commodities')
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) > 0


def test_create_commodity_with_properties(test_client):
    """Test creating a commodity along with properties"""
    response = test_client.post('/inventory/commodities/full', json={
        "name": "Magic Shield",
        "category": "enchanted defense",
        "properties": [
            {"property_name": CommodityPropertyType.COLOR.value, "property_value": "Golden"},
            {"property_name": CommodityPropertyType.MATERIAL.value, "property_value": "Adamantium"}
        ]
    })
    assert response.status_code == 201
    assert "commodity" in response.json
    assert "properties" in response.json["commodity"]
    assert len(response.json["commodity"]["properties"]) > 0


def test_get_single_commodity(test_client, setup_data):
    """Test retrieving a single commodity"""
    response = test_client.get(f'/inventory/commodities/{setup_data["sword_id"]}')
    assert response.status_code == 200
    assert "id" in response.json
    assert "name" in response.json
    assert "category" in response.json


def test_update_commodity(test_client, setup_data):
    """Test updating a commodity"""
    response = test_client.put(f'/inventory/commodities/{setup_data["shield_id"]}', json={
        "name": "Magic Shield",
        "category": "enchanted defense"
    })
    assert response.status_code == 200
    assert response.json["message"] == SUCCESS_COMMODITY_UPDATED


def test_delete_commodity(test_client, setup_data):
    """Test deleting a commodity"""
    response = test_client.delete(f'/inventory/commodities/{setup_data["sword_id"]}')
    assert response.status_code == 200
    assert response.json["message"] == SUCCESS_COMMODITY_DELETED


def test_create_property(test_client, setup_data):
    """Test creating a property for a commodity"""
    response = test_client.post(f'/inventory/commodities/{setup_data["shield_id"]}/properties', json={
        "property_name": CommodityPropertyType.COLOR.value,
        "property_value": "Blue"
    })
    assert response.status_code == 201
    assert "property_id" in response.json


def test_get_properties(test_client, setup_data):
    """Test retrieving all properties of a commodity"""
    test_client.post(f'/inventory/commodities/{setup_data["shield_id"]}/properties', json={
        "property_name": CommodityPropertyType.MATERIAL.value,
        "property_value": "Steel"
    })
    response = test_client.get(f'/inventory/commodities/{setup_data["shield_id"]}/properties')
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) > 0


def test_get_single_property(test_client, setup_data):
    """Test retrieving a single property"""
    property_response = test_client.post(f'/inventory/commodities/{setup_data["shield_id"]}/properties', json={
        "property_name": CommodityPropertyType.MATERIAL.value,
        "property_value": "Steel"
    })
    property_id = property_response.json.get("property_id")

    response = test_client.get(f'/inventory/commodities/properties/{property_id}')
    assert response.status_code == 200
    assert "property_name" in response.json
    assert "property_value" in response.json


def test_update_property(test_client, setup_data):
    """Test updating a commodity property"""
    property_response = test_client.post(f'/inventory/commodities/{setup_data["shield_id"]}/properties', json={
        "property_name": CommodityPropertyType.SIZE.value,
        "property_value": "Medium"
    })
    property_id = property_response.json.get("property_id")

    response = test_client.put(f'/inventory/commodities/properties/{property_id}', json={
        "property_name": CommodityPropertyType.SIZE.value,
        "property_value": "Large"
    })
    assert response.status_code == 200
    assert response.json["message"] == SUCCESS_PROPERTY_UPDATED


def test_delete_property(test_client, setup_data):
    """Test deleting a commodity property"""
    property_response = test_client.post(f'/inventory/commodities/{setup_data["shield_id"]}/properties', json={
        "property_name": CommodityPropertyType.MATERIAL.value,
        "property_value": "Iron"
    })
    property_id = property_response.json.get("property_id")

    response = test_client.delete(f'/inventory/commodities/properties/{property_id}')
    assert response.status_code == 200
    assert response.json["message"] == SUCCESS_PROPERTY_DELETED


def test_add_inventory(test_client, setup_data):
    """Test adding items to a trader's inventory"""
    response = test_client.post('/inventory', json={
        "trader_id": setup_data["trader_id"],
        "commodity_id": setup_data["sword_id"],
        "quantity": 10
    })
    assert response.status_code == 201
    assert response.json["message"] == SUCCESS_INVENTORY_UPDATED

def test_get_inventory(test_client, setup_data):
    """Test retrieving trader inventory"""
    test_client.post('/inventory', json={
        "trader_id": setup_data["trader_id"],
        "commodity_id": setup_data["sword_id"],
        "quantity": 5
    })
    response = test_client.get(f'/inventory/{setup_data["trader_id"]}')
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) > 0
