from flask import Blueprint, jsonify, request
from app.models import PropertyRepository
from app.services.ai_service import AIPropertySearch
from app.services.ml_service import ml_service

api_bp = Blueprint('api', __name__)

@api_bp.route('/properties')
def get_properties():
    """API endpoint for properties"""
    properties = PropertyRepository.load_properties()
    return jsonify(properties)

@api_bp.route('/search_properties', methods=['POST'])
def search_properties():
    """Enhanced AI-powered property search with deterministic filtering"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({
                'properties': PropertyRepository.load_properties()[:6],
                'explanation': 'Menampilkan beberapa properti terbaru.',
                'ai_powered': False
            })
        
        # Use the new AI search service
        result = AIPropertySearch.search_properties(query)
        return jsonify(result)
        
    except Exception as e:
        # Fallback to basic properties on error
        return jsonify({
            'properties': PropertyRepository.load_properties()[:5],
            'explanation': 'Terjadi kesalahan dalam pencarian. Menampilkan properti terbaru.',
            'ai_powered': False,
            'error': str(e)
        })

@api_bp.route('/predict', methods=['POST'])
def predict_price():
    """API endpoint for price prediction"""
    try:
        data = request.get_json()
        prediction = ml_service.predict_price(data)
        
        if prediction:
            return jsonify({
                'prediction': prediction, 
                'formatted': f"Rp {prediction:,.0f}"
            })
        else:
            return jsonify({
                'error': 'Cannot predict price with current data. Please check if all required fields are provided.'
            }), 400
    except Exception as e:
        return jsonify({
            'error': f'Prediction failed: {str(e)}'
        }), 500