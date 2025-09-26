from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import PropertyRepository
from app.services.ai_service import gemini_chat_response
from app.services.ml_service import ml_service

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Homepage with search functionality"""
    properties = PropertyRepository.load_properties()
    featured_properties = properties[:6]  # Show first 6 as featured
    return render_template('index.html', properties=featured_properties)

@main_bp.route('/properties')
def properties():
    """Property listings page"""
    properties = PropertyRepository.load_properties()
    
    # Apply filters
    budget_min = request.args.get('budget_min', type=int)
    budget_max = request.args.get('budget_max', type=int)
    kamar_tidur = request.args.get('kamar_tidur', type=int)
    
    filtered_properties = properties
    if budget_min:
        filtered_properties = [p for p in filtered_properties if p.get('harga', 0) >= budget_min]
    if budget_max:
        filtered_properties = [p for p in filtered_properties if p.get('harga', 0) <= budget_max]
    if kamar_tidur:
        filtered_properties = [p for p in filtered_properties if p.get('kamar_tidur', 0) >= kamar_tidur]
    
    return render_template('properties.html', properties=filtered_properties)

@main_bp.route('/property/<property_id>')
def property_detail(property_id):
    """Property detail page"""
    property_data = PropertyRepository.get_property_by_id(property_id)
    
    if not property_data:
        flash('Property not found')
        return redirect(url_for('main.properties'))
    
    # Get similar properties
    all_properties = PropertyRepository.load_properties()
    similar_properties = [p for p in all_properties if p['id'] != property_id][:3]
    
    return render_template('property_detail.html', property=property_data, similar_properties=similar_properties)

@main_bp.route('/predict', methods=['GET', 'POST'])
def price_prediction():
    """Price prediction page"""
    price_range = None
    
    if request.method == 'POST':
        property_data = {
            'luas_tanah': request.form.get('luas_tanah'),
            'luas_bangunan': request.form.get('luas_bangunan'),
            'kamar_tidur': request.form.get('kamar_tidur'),
            'kamar_mandi': request.form.get('kamar_mandi'),
            'carport': request.form.get('carport', 0),
            'tahun_dibangun': request.form.get('tahun_dibangun', 2020),
            'jarak_sekolah': request.form.get('jarak_sekolah', 1000),
            'jarak_rs': request.form.get('jarak_rs', 2000),
            'jarak_pasar': request.form.get('jarak_pasar', 1500),
            'jenis_jalan': request.form.get('jenis_jalan'),
            'kondisi': request.form.get('kondisi'),
            'sertifikat': request.form.get('sertifikat', 'hgb')
        }
        
        prediction_range = ml_service.get_price_range(property_data)
        if prediction_range:
            price_range = {
                'predicted': prediction_range['predicted_price'],
                'min': prediction_range['min_price'],
                'max': prediction_range['max_price'],
                'formatted_predicted': f"Rp {prediction_range['predicted_price']:,.0f}",
                'formatted_min': f"Rp {prediction_range['min_price']:,.0f}",
                'formatted_max': f"Rp {prediction_range['max_price']:,.0f}"
            }
    
    return render_template('predict.html', price_range=price_range)

@main_bp.route('/chat', methods=['GET', 'POST'])
def chat():
    """Chatbot page"""
    if request.method == 'POST':
        message = request.form.get('message')
        if message:
            response = gemini_chat_response(message)
            return {'response': response}
    
    return render_template('chat.html')