from alembic import op

# Revision identifiers
revision = '81779120f65f'
down_revision = '81779120f64e'  # Ensuring the order is correct
branch_labels = None
depends_on = None

def upgrade():
    """Ensure tables exist before creating materialized views."""

    op.execute("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS trade_acceptance_rate AS
        SELECT
            tr.trader_type,
            COUNT(CASE WHEN t.status = 'accepted' THEN 1 END) * 1.0 / COUNT(*) AS acceptance_rate
        FROM trader tr
        JOIN trade t ON tr.id = t.traded_from
        WHERE t.created_at >= NOW() - INTERVAL '1 month'
        GROUP BY tr.trader_type;
    """)

    op.execute("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS market_conversion_rates AS
        WITH trade_data AS (
            SELECT
                t.id AS trade_id,
                ARRAY_AGG(c1.name ORDER BY tc1.commodity_id) AS offered_items,
                ARRAY_AGG(tc1.quantity ORDER BY tc1.commodity_id) AS offered_quantities,
                ARRAY_AGG(c2.name ORDER BY tc2.commodity_id) AS requested_items,
                ARRAY_AGG(tc2.quantity ORDER BY tc2.commodity_id) AS requested_quantities
            FROM trade t
            JOIN trade_commodity tc1 ON t.id = tc1.trade_id AND tc1.role = 'offer'
            JOIN commodity c1 ON tc1.commodity_id = c1.id
            JOIN trade_commodity tc2 ON t.id = tc2.trade_id AND tc2.role = 'request'
            JOIN commodity c2 ON tc2.commodity_id = c2.id
            WHERE t.status = 'accepted'
                AND t.created_at >= NOW() - INTERVAL '1 month'
            GROUP BY t.id
        )
        SELECT
            offered_items,
            offered_quantities,
            requested_items,
            requested_quantities,
            COUNT(distinct trade_id) AS trade_count
        FROM trade_data
        GROUP BY offered_items, offered_quantities, requested_items, requested_quantities
        ORDER BY trade_count DESC;
    """)

    op.execute("CREATE INDEX IF NOT EXISTS idx_trade_status ON trade (status);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_trade_created_at ON trade (created_at);")

def downgrade():
    """Drop Materialized Views if rollback occurs"""

    op.execute("DROP INDEX IF EXISTS idx_trade_status;")
    op.execute("DROP INDEX IF EXISTS idx_trade_created_at;")

    op.execute("DROP MATERIALIZED VIEW IF EXISTS trade_acceptance_rate CASCADE;")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS market_conversion_rates CASCADE;")

