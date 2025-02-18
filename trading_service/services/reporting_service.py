from trading_service.database import db
from sqlalchemy import text

def get_trade_acceptance_report():
    """Fetch precomputed trade acceptance rate from materialized view."""
    result = db.session.execute(text("SELECT * FROM trade_acceptance_rate;")).fetchall()
    return [{"trader_type": row[0], "acceptance_rate": row[1]} for row in result]

def get_market_conversion_report():
    """Fetch precomputed market conversion rates from materialized view."""
    query = text("SELECT * FROM market_conversion_rates;")
    result = db.session.execute(query)
    trades = result.fetchall()

    trade_data = []
    for row in trades:
        trade_data.append({
            "offered_items": row[0],  # Offered item names
            "offered_quantities": row[1],  # Corresponding quantities
            "requested_items": row[2],  # Requested item names
            "requested_quantities": row[3],  # Corresponding quantities
            "trade_count": row[4],  # How many times this trade happened
        })

    return trade_data