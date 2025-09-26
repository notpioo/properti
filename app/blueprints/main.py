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
    prediction = None
    
    if request.method == 'POST':
        property_data = {
            'luas_tanah': request.form.get('luas_tanah'),
            'luas_bangunan': request.form.get('luas_bangunan'),
            'kamar_tidur': request.form.get('kamar_tidur'),
            'kamar_mandi': request.form.get('kamar_mandi'),
            'carport': request.form.get('carport'),
            'tahun_dibangun': request.form.get('tahun_dibangun'),
            'jarak_sekolah': request.form.get('jarak_sekolah'),
            'jarak_rs': request.form.get('jarak_rs'),
            'jarak_pasar': request.form.get('jarak_pasar'),
            'jenis_jalan': request.form.get('jenis_jalan'),
            'kondisi': request.form.get('kondisi'),
            'sertifikat': request.form.get('sertifikat')
        }
        
        prediction_value = ml_service.predict_price(property_data)
        if prediction_value:
            prediction = f"Rp {prediction_value:,.0f}"
    
    return render_template('predict.html', prediction=prediction)

@main_bp.route('/chat', methods=['GET', 'POST'])
def chat():
    """Chatbot page"""
    if request.method == 'POST':
        message = request.form.get('message')
        if message:
            response = gemini_chat_response(message)
            return {'response': response}
    
    return render_template('chat.html')