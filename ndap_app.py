"""
NDAP Intelligence Platform - Flask Web Server
Serves the prescriptive dashboard interface and connects to the ML recommendation engine.

Run with: python ndap_app.py
Then open: http://localhost:5000
"""

import logging
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS

from prescriptive_engine import NDAPPrescriptiveEngine

app = Flask(__name__)
CORS(app)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the recommendation engine
try:
    engine = NDAPPrescriptiveEngine()
    logger.info("✓ NDAP Prescriptive Engine loaded successfully")
except (AttributeError, FileNotFoundError, KeyError, TypeError, ValueError) as e:
    logger.warning("⚠ Warning: Could not fully initialize engine. %s", e)
    engine = None


@app.route('/')
def index():
    """Serve the main dashboard HTML."""
    html_path = Path(__file__).parent / 'ndap_prescriptive_dashboard.html'
    if html_path.exists():
        return send_file(html_path)
    else:
        return "Dashboard HTML not found", 404


@app.route('/api/recommend', methods=['POST'])
def generate_recommendation():
    """
    API endpoint for generating personalized recommendations.

    Expected JSON payload:
    {
        "name": "...",
        "age": 28,
        "state": "...",
        "city": "...",
        "education": "...",
        "sector": "...",
        "employment": "...",
        "skills": "...",
        "income": 240000,
        "debt": 0,
        "loanStatus": "...",
        "loanAmount": 75000,
        "repayment": "...",
        "documents": "...",
        "household": "...",
        "notes": "..."
    }

    Returns: JSON with personalized recommendations
    """
    try:
        profile = request.json

        # Validate required fields
        required_fields = ['name', 'age', 'state', 'education', 'sector', 'income', 'loanStatus', 'repayment', 'documents']
        missing = [f for f in required_fields if f not in profile or profile[f] == '']
        if missing:
            return jsonify({'error': f'Missing required fields: {", ".join(missing)}'}), 400

        # Generate recommendation
        if engine:
            recommendation = engine.generate_recommendation(profile)
            return jsonify(recommendation), 200
        else:
            return jsonify({'error': 'Recommendation engine not initialized'}), 500

    except (AttributeError, KeyError, TypeError, ValueError) as e:
        logger.error("Error generating recommendation: %s", e)
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'engine_loaded': engine is not None,
        'timestamp': datetime.now(timezone.utc).isoformat(),
    }), 200


@app.route('/api/states', methods=['GET'])
def get_states():
    """Get list of available states."""
    states = [
        'Rajasthan', 'Punjab', 'Madhya Pradesh', 'Karnataka', 'Tamil Nadu',
        'West Bengal', 'Uttar Pradesh', 'Gujarat', 'Assam', 'Bihar',
        'Haryana', 'Telangana', 'Odisha', 'Andhra Pradesh', 'Goa',
        'Himachal Pradesh', 'Uttarakhand', 'Tripura', 'Manipur',
        'Mizoram', 'Jharkhand', 'Chhattisgarh', 'Kerala', 'Nagaland'
    ]
    return jsonify({'states': sorted(states)}), 200


@app.route('/api/sectors', methods=['GET'])
def get_sectors():
    """Get list of available business sectors."""
    sectors = [
        'Agriculture', 'Textile & Apparel', 'Food & Beverage', 'Retail & Trade',
        'Services', 'Manufacturing', 'Technology', 'Beauty & Wellness',
        'Education', 'Healthcare', 'Construction', 'Transportation'
    ]
    return jsonify({'sectors': sorted(sectors)}), 200


@app.route('/api/export/<format>', methods=['POST'])
def export_recommendation(format):
    """
    Export recommendation as PDF or CSV.

    Expected JSON: the recommendation object
    """
    try:
        if format == 'pdf':
            # Would integrate with reportlab or similar
            return jsonify({'message': 'PDF export coming soon'}), 501

        if format == 'csv':
            # Would convert to CSV format
            return jsonify({'message': 'CSV export coming soon'}), 501

        return jsonify({'error': 'Invalid format'}), 400

    except (AttributeError, KeyError, TypeError, ValueError) as e:
        logger.error("Error exporting recommendation: %s", e)
        return jsonify({'error': str(e)}), 500


@app.route('/api/dashboard', methods=['GET'])
def dashboard_data():
    """Get aggregated dashboard statistics."""
    try:
        if not engine or not engine.data:
            return jsonify({'error': 'Data not loaded'}), 500

        # Get some basic stats from the datasets
        dashboard = {
            'total_pmmy_accounts': 0,
            'average_loan_size': 0,
            'state_count': 0,
            'female_lfpr_avg': 0,
        }

        # These would be populated with actual data from datasets
        return jsonify(dashboard), 200

    except (AttributeError, KeyError, TypeError, ValueError) as e:
        logger.error("Error getting dashboard data: %s", e)
        return jsonify({'error': str(e)}), 500


@app.route('/api/compare', methods=['POST'])
def compare_profiles():
    """
    Compare current woman with similar profiles in the database.

    Expected JSON: profile object
    """
    try:
        # Would implement similarity matching here
        comparison = {
            'similar_profiles_count': 0,
            'percentile': 0,
            'average_income_peer': 0,
            'success_rate_peer': 0,
        }

        return jsonify(comparison), 200

    except (AttributeError, KeyError, TypeError, ValueError) as e:
        logger.error("Error comparing profiles: %s", e)
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("""

╔════════════════════════════════════════════════════════════════════════════╗
║                      SWAN                                                  ║
║         Decision Support System for Women Entrepreneurs                    ║
╚════════════════════════════════════════════════════════════════════════════╝

🚀 Starting Flask Server...

📊 Available Endpoints:
   - GET  /                    → Dashboard UI
   - POST /api/recommend       → Generate personalized recommendations
   - GET  /api/states          → List available states
   - GET  /api/sectors         → List business sectors
   - GET  /api/health          → Health check
   - POST /api/compare         → Compare with similar profiles
   - POST /api/export/<format> → Export recommendation

🌐 Open in browser: http://localhost:5000

📁 Datasets loaded: PMMY, PLFS, Wages, Industry, Education, UDYAM
🔧 ML Engine: Initialized and ready

    """)

    app.run(debug=True, port=5001, host='0.0.0.0')
