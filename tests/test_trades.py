import pytest
from app.models.trader_models import TraderType


@pytest.fixture(scope="function")
def setup_trade_data(test_client):
    """Set up traders, commodities, and inventories before running trade tests"""

    trader1 = test_client.post('/traders', json={"name": "Yogesh", "trader_type": "elf"})
    trader2 = test_client.post('/traders', json={"name": "Singh", "trader_type": "dwarf"})

    assert trader1.status_code == 201, f"Trader1 creation failed: {trader1.json if trader1.is_json else trader1.text}"
    assert trader2.status_code == 201, f"Trader2 creation failed: {trader2.json if trader2.is_json else trader2.text}"

    trader1_id = trader1.json.get("trader_id") if trader1.is_json else None
    trader2_id = trader2.json.get("trader_id") if trader2.is_json else None

    assert trader1_id is not None, "Trader1 ID is missing"
    assert trader2_id is not None, "Trader2 ID is missing"

    sword = test_client.post('/inventory/commodities', json={"name": "Sword", "category": "weapon"})
    axe = test_client.post('/inventory/commodities', json={"name": "Axe", "category": "weapon"})

    assert sword.status_code == 201, f"Sword creation failed: {sword.json if sword.is_json else sword.text}"
    assert axe.status_code == 201, f"Axe creation failed: {axe.json if axe.is_json else axe.text}"

    sword_id = sword.json.get('commodity').get("id") if sword.is_json else None
    axe_id = axe.json.get('commodity').get("id") if axe.is_json else None

    assert sword_id is not None, "Sword ID is missing"
    assert axe_id is not None, "Axe ID is missing"

    trader1_inventory = test_client.post('/inventory', json={"trader_id": trader1_id, "commodity_id": sword_id, "quantity": 10})
    trader2_inventory = test_client.post('/inventory', json={"trader_id": trader2_id, "commodity_id": axe_id, "quantity": 5})

    assert trader1_inventory.status_code == 201, f"Trader1 inventory creation failed: {trader1_inventory.json if trader1_inventory.is_json else trader1_inventory.text}"
    assert trader2_inventory.status_code == 201, f"Trader2 inventory creation failed: {trader2_inventory.json if trader2_inventory.is_json else trader2_inventory.text}"

    return {"trader1_id": trader1_id, "trader2_id": trader2_id, "sword_id": sword_id, "axe_id": axe_id}


def test_create_trade(test_client, setup_trade_data):
    """Test creating a trade request successfully"""
    response = test_client.post('/trades/trade', json={
        "traded_from": setup_trade_data["trader1_id"],
        "traded_to": setup_trade_data["trader2_id"],
        "offered_items": [{"commodity_id": setup_trade_data["sword_id"], "quantity": 3}],
        "requested_items": [{"commodity_id": setup_trade_data["axe_id"], "quantity": 2}]
    })

    assert response.status_code == 201, f"Trade creation failed: {response.json if response.is_json else response.text}"
    assert "trade_id" in response.json


def test_create_trade_with_insufficient_inventory(test_client, setup_trade_data):
    """Test creating a trade where sender lacks inventory"""
    response = test_client.post('/trades/trade', json={
        "traded_from": setup_trade_data["trader1_id"],
        "traded_to": setup_trade_data["trader2_id"],
        "offered_items": [{"commodity_id": setup_trade_data["sword_id"], "quantity": 20}],
        "requested_items": [{"commodity_id": setup_trade_data["axe_id"], "quantity": 2}]
    })

    assert response.status_code == 400, f"Unexpected response: {response.json if response.is_json else response.text}"
    assert response.json["error"] == "Sender does not have sufficient commodities"


def test_accept_trade(test_client, setup_trade_data):
    """Test accepting a trade successfully"""
    trade_response = test_client.post('/trades/trade', json={
        "traded_from": setup_trade_data["trader1_id"],
        "traded_to": setup_trade_data["trader2_id"],
        "offered_items": [{"commodity_id": setup_trade_data["sword_id"], "quantity": 3}],
        "requested_items": [{"commodity_id": setup_trade_data["axe_id"], "quantity": 2}]
    })

    trade_id = trade_response.json.get("trade_id") if trade_response.is_json else None
    assert trade_id, f"Trade ID missing from response: {trade_response.text}"

    response = test_client.post(f'/trades/trade/{trade_id}/response', json={"response": "accept"})
    assert response.status_code == 200, f"Trade acceptance failed: {response.json if response.is_json else response.text}"


def test_reject_trade(test_client, setup_trade_data):
    """Test rejecting a trade"""
    trade_response = test_client.post('/trades/trade', json={
        "traded_from": setup_trade_data["trader1_id"],
        "traded_to": setup_trade_data["trader2_id"],
        "offered_items": [{"commodity_id": setup_trade_data["sword_id"], "quantity": 3}],
        "requested_items": [{"commodity_id": setup_trade_data["axe_id"], "quantity": 2}]
    })

    trade_id = trade_response.json.get("trade_id") if trade_response.is_json else None
    assert trade_id, f"Trade ID missing from response: {trade_response.text}"

    response = test_client.post(f'/trades/trade/{trade_id}/response', json={"response": "reject"})
    assert response.status_code == 200


def test_reverse_trade(test_client, setup_trade_data):
    """Test reversing a completed trade"""
    trade_response = test_client.post('/trades/trade', json={
        "traded_from": setup_trade_data["trader1_id"],
        "traded_to": setup_trade_data["trader2_id"],
        "offered_items": [{"commodity_id": setup_trade_data["sword_id"], "quantity": 3}],
        "requested_items": [{"commodity_id": setup_trade_data["axe_id"], "quantity": 2}]
    })

    trade_id = trade_response.json.get("trade_id") if trade_response.is_json else None
    assert trade_id, f"Trade ID missing from response: {trade_response.text}"

    test_client.post(f'/trades/trade/{trade_id}/response', json={"response": "accept"})

    response = test_client.post(f'/trades/trade/{trade_id}/reverse', json={"reason": "Item was defective"})
    assert response.status_code == 200


def test_reverse_already_reversed_trade(test_client, setup_trade_data):
    """Test reversing a trade that has already been reversed"""
    trade_response = test_client.post('/trades/trade', json={
        "traded_from": setup_trade_data["trader1_id"],
        "traded_to": setup_trade_data["trader2_id"],
        "offered_items": [{"commodity_id": setup_trade_data["sword_id"], "quantity": 3}],
        "requested_items": [{"commodity_id": setup_trade_data["axe_id"], "quantity": 2}]
    })

    trade_id = trade_response.json.get("trade_id") if trade_response.is_json else None
    assert trade_id, f"Trade ID missing from response: {trade_response.text}"


    test_client.post(f'/trades/trade/{trade_id}/response', json={"response": "accept"})
    test_client.post(f'/trades/trade/{trade_id}/reverse', json={"reason": "Item was defective"})

    response = test_client.post(f'/trades/trade/{trade_id}/reverse', json={"reason": "Second reversal"})
    assert response.status_code == 400
