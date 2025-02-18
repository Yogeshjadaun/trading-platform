from app.models.inventory_models import TraderInventory

def has_sufficient_inventory(trader_id, commodities):
    """Check if trader has required commodities in sufficient quantity."""
    for item in commodities:
        inventory = TraderInventory.query.filter_by(trader_id=trader_id, commodity_id=item["commodity_id"]).first()
        if not inventory or inventory.quantity < item["quantity"]:
            return False
    return True
