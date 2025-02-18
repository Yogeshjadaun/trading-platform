from flask import Blueprint, jsonify
from trading_service.services.reporting_service import get_trade_acceptance_report, get_market_conversion_report
from trading_service.tasks.reporting_tasks import refresh_materialized_views, refresh_materialized_views_data

reporting_bp = Blueprint('reporting', __name__)

@reporting_bp.route('/monthly', methods=['GET'])
def get_monthly_report():
    """Retrieve precomputed monthly trade reports from materialized views."""
    return jsonify({
        "acceptance_rates": get_trade_acceptance_report(),
        "conversion_rates": get_market_conversion_report()
    }), 200

@reporting_bp.route('/refresh', methods=['POST'])
def trigger_manual_refresh():
    """Manually refresh materialized views via Celery."""
    refresh_materialized_views.delay()
    return jsonify({"message": "Materialized view refresh scheduled"}), 202

@reporting_bp.route('/refresh/sync', methods=['POST'])
def trigger_manual_refresh_sync():
    """Manually refresh materialized views."""
    refresh_materialized_views_data()
    return jsonify({"message": "Materialized view refreshed"}), 200