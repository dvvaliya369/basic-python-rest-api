"""Health check route for database and API status"""

from flask import jsonify
from api import app
from api.database import check_database_health


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify API and database status"""
    try:
        # Check database health
        db_status = check_database_health()
        
        # Overall API health
        api_status = {
            'status': 'healthy',
            'message': 'API is running',
            'version': '1.0.0'
        }
        
        # Combined response
        response = {
            'api': api_status,
            'database': db_status,
            'overall_status': 'healthy' if db_status['status'] == 'healthy' else 'degraded'
        }
        
        status_code = 200 if db_status['status'] == 'healthy' else 503
        
        return jsonify(response), status_code
        
    except Exception as e:
        app.logger.exception(f'Health check failed: {str(e)}')
        return jsonify({
            'api': {'status': 'error', 'message': str(e)},
            'database': {'status': 'unknown', 'message': 'Could not check database'},
            'overall_status': 'error'
        }), 500
