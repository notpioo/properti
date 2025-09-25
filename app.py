import os
import json
import uuid
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import pickle
from dotenv import load_dotenv

# Import Gemini AI integration - references blueprint:python_gemini integration
from gemini import client, types
from google import genai

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SESSION_SECRET', 'your-secret-key-here')
app.config['UPLOAD_FOLDER'] = 'static/images'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('data', exist_ok=True)
os.makedirs('models', exist_ok=True)

# Global variables for ML model
ml_model = None
scaler = None
feature_columns = ['luas_tanah', 'luas_bangunan', 'kamar_tidur', 'kamar_mandi', 
                  'carport', 'tahun_dibangun', 'jarak_sekolah', 'jarak_rs', 
                  'jarak_pasar', 'jenis_jalan_encoded', 'kondisi_encoded', 'sertifikat_encoded']

def load_properties():
    """Load properties from JSON file"""
    try:
        with open('data/properties.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_properties(properties):
    """Save properties to JSON file"""
    with open('data/properties.json', 'w') as f:
        json.dump(properties, f, indent=2)

def encode_categorical(value, mapping):
    """Encode categorical values"""
    return mapping.get(value, 0)

def prepare_ml_data():
    """Prepare data for machine learning"""
    properties = load_properties()
    if len(properties) < 5:  # Need minimum data for training
        return None
    
    # Create mappings for categorical variables
    jenis_jalan_map = {'gang_kecil': 1, 'jalan_sedang': 2, 'jalan_besar': 3}
    kondisi_map = {'butuh_renovasi': 1, 'renovasi_ringan': 2, 'baik': 3, 'baru': 4}
    sertifikat_map = {'lainnya': 1, 'HGB': 2, 'SHM': 3}
    
    # Prepare dataset
    data = []
    for prop in properties:
        if prop.get('harga') and all(key in prop for key in ['luas_tanah', 'luas_bangunan']):
            row = [
                float(prop['luas_tanah']),
                float(prop['luas_bangunan']),
                int(prop.get('kamar_tidur', 2)),
                int(prop.get('kamar_mandi', 1)),
                int(prop.get('carport', 0)),
                int(prop.get('tahun_dibangun', 2020)),
                float(prop.get('jarak_sekolah', 1000)),
                float(prop.get('jarak_rs', 2000)),
                float(prop.get('jarak_pasar', 1500)),
                encode_categorical(prop.get('jenis_jalan'), jenis_jalan_map),
                encode_categorical(prop.get('kondisi'), kondisi_map),
                encode_categorical(prop.get('sertifikat'), sertifikat_map),
                float(prop['harga'])
            ]
            data.append(row)
    
    if len(data) < 5:
        return None
        
    columns = feature_columns + ['harga']
    df = pd.DataFrame(data, columns=columns)
    return df

def train_ml_model():
    """Train the machine learning model"""
    global ml_model, scaler
    
    df = prepare_ml_data()
    if df is None:
        return False
    
    # Prepare features and target
    X = df[feature_columns]
    y = df['harga']
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Train model
    ml_model = RandomForestRegressor(n_estimators=100, random_state=42)
    ml_model.fit(X_scaled, y)
    
    # Save model
    with open('models/price_model.pkl', 'wb') as f:
        pickle.dump({'model': ml_model, 'scaler': scaler}, f)
    
    return True

def load_ml_model():
    """Load the trained ML model"""
    global ml_model, scaler
    try:
        with open('models/price_model.pkl', 'rb') as f:
            model_data = pickle.load(f)
            ml_model = model_data['model']
            scaler = model_data['scaler']
        return True
    except FileNotFoundError:
        return train_ml_model()

def predict_price(property_data):
    """Predict house price using ML model"""
    global ml_model, scaler
    
    if ml_model is None:
        if not load_ml_model():
            return None
    
    # Prepare input data
    jenis_jalan_map = {'gang_kecil': 1, 'jalan_sedang': 2, 'jalan_besar': 3}
    kondisi_map = {'butuh_renovasi': 1, 'renovasi_ringan': 2, 'baik': 3, 'baru': 4}
    sertifikat_map = {'lainnya': 1, 'HGB': 2, 'SHM': 3}
    
    features = [
        float(property_data.get('luas_tanah', 100)),
        float(property_data.get('luas_bangunan', 80)),
        int(property_data.get('kamar_tidur', 2)),
        int(property_data.get('kamar_mandi', 1)),
        int(property_data.get('carport', 0)),
        int(property_data.get('tahun_dibangun', 2020)),
        float(property_data.get('jarak_sekolah', 1000)),
        float(property_data.get('jarak_rs', 2000)),
        float(property_data.get('jarak_pasar', 1500)),
        encode_categorical(property_data.get('jenis_jalan'), jenis_jalan_map),
        encode_categorical(property_data.get('kondisi'), kondisi_map),
        encode_categorical(property_data.get('sertifikat'), sertifikat_map)
    ]
    
    # Scale and predict
    if scaler is not None and ml_model is not None:
        features_scaled = scaler.transform([features])
        prediction = ml_model.predict(features_scaled)[0]
    else:
        return None
    
    return max(0, prediction)  # Ensure non-negative price

def gemini_chat_response(message, context=None):
    """Generate chatbot response using Gemini AI - references blueprint:python_gemini integration"""
    try:
        # Create context about properties
        properties = load_properties()
        property_context = f"Available properties count: {len(properties)}"
        if properties:
            avg_price = sum(float(p.get('harga', 0)) for p in properties if p.get('harga')) / len([p for p in properties if p.get('harga')])
            property_context += f", Average price: Rp {avg_price:,.0f}"
        
        system_prompt = f"""You are a helpful real estate assistant for a property recommendation system. 
        Context: {property_context}
        
        Help users with:
        - Property searches and recommendations
        - Price predictions and market analysis
        - Location and facility information
        - Answering questions about property features
        
        Be friendly, informative, and helpful. Respond in Bahasa Indonesia when appropriate."""
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Content(role="user", parts=[types.Part(text=f"{system_prompt}\n\nUser question: {message}")])
            ]
        )
        
        return response.text if response.text else "Maaf, saya tidak dapat memproses pertanyaan Anda saat ini."
        
    except Exception as e:
        return "Maaf, terjadi kesalahan pada sistem chatbot. Silakan coba lagi."

@app.route('/')
def index():
    """Homepage with search functionality"""
    properties = load_properties()
    featured_properties = properties[:6]  # Show first 6 as featured
    return render_template('index.html', properties=featured_properties)

@app.route('/properties')
def properties():
    """Property listings page"""
    properties = load_properties()
    
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

@app.route('/property/<property_id>')
def property_detail(property_id):
    """Property detail page"""
    properties = load_properties()
    property_data = next((p for p in properties if p['id'] == property_id), None)
    
    if not property_data:
        flash('Property not found')
        return redirect(url_for('properties'))
    
    # Get similar properties
    similar_properties = [p for p in properties if p['id'] != property_id][:3]
    
    return render_template('property_detail.html', property=property_data, similar_properties=similar_properties)

@app.route('/predict', methods=['GET', 'POST'])
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
        
        prediction = predict_price(property_data)
        if prediction:
            prediction = f"Rp {prediction:,.0f}"
    
    return render_template('predict.html', prediction=prediction)

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    """Chatbot page"""
    if request.method == 'POST':
        message = request.form.get('message')
        if message:
            response = gemini_chat_response(message)
            return jsonify({'response': response})
    
    return render_template('chat.html')

@app.route('/admin')
def admin():
    """Admin panel for property management"""
    properties = load_properties()
    return render_template('admin.html', properties=properties)

@app.route('/admin/add_property', methods=['POST'])
def add_property():
    """Add new property"""
    try:
        # Handle file upload
        image_filename = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                filename = secure_filename(file.filename)
                image_filename = f"{uuid.uuid4()}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
        
        # Create property data
        property_data = {
            'id': str(uuid.uuid4()),
            'luas_tanah': int(request.form.get('luas_tanah') or 0),
            'luas_bangunan': int(request.form.get('luas_bangunan') or 0),
            'kamar_tidur': int(request.form.get('kamar_tidur') or 2),
            'kamar_mandi': int(request.form.get('kamar_mandi') or 1),
            'carport': int(request.form.get('carport', 0) or 0),
            'tahun_dibangun': int(request.form.get('tahun_dibangun') or 2020),
            'alamat': request.form.get('alamat'),
            'harga': float(request.form.get('harga') or 0) if request.form.get('harga') else None,
            'latitude': float(request.form.get('latitude') or 0) if request.form.get('latitude') else None,
            'longitude': float(request.form.get('longitude') or 0) if request.form.get('longitude') else None,
            'jarak_sekolah': float(request.form.get('jarak_sekolah', 1000) or 1000),
            'jarak_rs': float(request.form.get('jarak_rs', 2000) or 2000),
            'jarak_pasar': float(request.form.get('jarak_pasar', 1500) or 1500),
            'jenis_jalan': request.form.get('jenis_jalan'),
            'kondisi': request.form.get('kondisi'),
            'sertifikat': request.form.get('sertifikat'),
            'image': image_filename,
            'created_at': datetime.now().isoformat(),
            'status': 'available'
        }
        
        # Save property
        properties = load_properties()
        properties.append(property_data)
        save_properties(properties)
        
        # Retrain ML model with new data
        train_ml_model()
        
        flash('Property added successfully!')
        
    except Exception as e:
        flash(f'Error adding property: {str(e)}')
    
    return redirect(url_for('admin'))

@app.route('/admin/delete_property/<property_id>')
def delete_property(property_id):
    """Delete property"""
    properties = load_properties()
    properties = [p for p in properties if p['id'] != property_id]
    save_properties(properties)
    
    # Retrain model
    train_ml_model()
    
    flash('Property deleted successfully!')
    return redirect(url_for('admin'))

@app.route('/api/properties')
def api_properties():
    """API endpoint for properties"""
    properties = load_properties()
    return jsonify(properties)

@app.route('/api/predict', methods=['POST'])
def api_predict():
    """API endpoint for price prediction"""
    data = request.get_json()
    prediction = predict_price(data)
    
    if prediction:
        return jsonify({'prediction': prediction, 'formatted': f"Rp {prediction:,.0f}"})
    else:
        return jsonify({'error': 'Cannot predict price with current data'}), 400

if __name__ == '__main__':
    # Initialize ML model on startup
    load_ml_model()
    app.run(host='0.0.0.0', port=5000, debug=True)