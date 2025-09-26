import uuid
import os
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
from app.models import PropertyRepository
from app.services.ml_service import ml_service

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/')
def admin_panel():
    """Admin panel dashboard"""
    properties = PropertyRepository.load_properties()
    return render_template('admin/dashboard.html', properties=properties)

@admin_bp.route('/properties')
def properties():
    """Properties management page"""
    properties = PropertyRepository.load_properties()
    return render_template('admin/properties.html', properties=properties)

@admin_bp.route('/add_property', methods=['POST'])
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
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], image_filename))
        
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
        PropertyRepository.add_property(property_data)
        
        # Retrain ML model with new data
        ml_service.train_model()
        
        flash('Property added successfully!')
        
    except Exception as e:
        flash(f'Error adding property: {str(e)}')
    
    return redirect(url_for('admin.admin_panel'))

@admin_bp.route('/delete_property/<property_id>')
def delete_property(property_id):
    """Delete property"""
    if PropertyRepository.delete_property(property_id):
        # Retrain model
        ml_service.train_model()
        flash('Property deleted successfully!')
    else:
        flash('Property not found')
    
    return redirect(url_for('admin.admin_panel'))