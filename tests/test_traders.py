from trading_service.models.trader_models import TraderType

def test_create_trader(test_client):
    """Test creating a new trader"""
    response = test_client.post('/traders', json={
        "name": "Yogesh",
        "trader_type": TraderType.ELF.value
    })
    assert response.status_code == 201
    assert response.json["message"] == "Trader created"
    assert "trader_id" in response.json


def test_get_traders(test_client):
    test_client.post('/traders', json={"name": "Yogesh", "trader_type": TraderType.WIZARD.value})
    """Test retrieving all traders"""
    response = test_client.get('/traders')
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) > 0
    assert "name" in response.json[0]
    assert "trader_type" in response.json[0]
