import pytest


@pytest.fixture(scope="function")
def setup_report_data(test_client):
    """Seed the database with test trades"""
    trader1 = test_client.post('/traders', json={"name": "Yogesh", "trader_type": "elf"})
    trader2 = test_client.post('/traders', json={"name": "Singh", "trader_type": "dwarf"})

    assert trader1.status_code == 201
    assert trader2.status_code == 201

    trader1_id = trader1.json["trader_id"]
    trader2_id = trader2.json["trader_id"]

    sword = test_client.post('/inventory/commodities', json={"name": "Sword", "category": "weapon"})
    shield = test_client.post('/inventory/commodities', json={"name": "Shield", "category": "defense"})
    axe = test_client.post('/inventory/commodities', json={"name": "Axe", "category": "weapon"})

    assert sword.status_code == 201
    assert shield.status_code == 201
    assert axe.status_code == 201

    sword_id = sword.json["commodity"]["id"]
    shield_id = shield.json["commodity"]["id"]
    axe_id = axe.json["commodity"]["id"]

    test_client.post('/inventory', json={"trader_id": trader1_id, "commodity_id": sword_id, "quantity": 5})
    test_client.post('/inventory', json={"trader_id": trader1_id, "commodity_id": shield_id, "quantity": 2})
    test_client.post('/inventory', json={"trader_id": trader2_id, "commodity_id": axe_id, "quantity": 4})

    trade_response = test_client.post('/trades/trade', json={
        "traded_from": trader1_id,
        "traded_to": trader2_id,
        "offered_items": [{"commodity_id": sword_id, "quantity": 2}, {"commodity_id": shield_id, "quantity": 1}],
        "requested_items": [{"commodity_id": axe_id, "quantity": 3}]
    })

    assert trade_response.status_code == 201
    trade_id = trade_response.json["trade_id"]

    accept_response = test_client.post(f'/trades/trade/{trade_id}/response', json={"response": "accept"})
    assert accept_response.status_code == 200


def test_get_monthly_reports(test_client, setup_report_data):
    """Test retrieving the detailed trade summary"""
    response = test_client.post('/reports/refresh/sync')
    assert response.status_code == 200

    response = test_client.get('/reports/monthly')

    assert response.status_code == 200
    assert "conversion_rates" in response.json
    assert "acceptance_rates" in response.json
    assert isinstance(response.json["conversion_rates"], list)
    assert isinstance(response.json["acceptance_rates"], list)
    assert len(response.json["conversion_rates"]) > 0
    assert len(response.json["acceptance_rates"]) > 0

    conversion_rates = response.json["conversion_rates"][0]
    assert "offered_items" in conversion_rates
    assert "offered_quantities" in conversion_rates
    assert "requested_items" in conversion_rates
    assert "requested_quantities" in conversion_rates
    assert "trade_count" in conversion_rates

    acceptance_rates = response.json["acceptance_rates"][0]
    assert "trader_type" in acceptance_rates
    assert "acceptance_rate" in acceptance_rates



def test_trigger_manual_refresh(test_client):
    """Test manually refreshing materialized views"""
    response = test_client.post('/reports/refresh')
    assert response.status_code == 202
    assert response.json["message"] == "Materialized view refresh scheduled"
