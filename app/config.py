import os

class Config:
    """Application configuration"""
    SECRET_KEY = os.environ.get('SESSION_SECRET')
    if not SECRET_KEY:
        raise ValueError("SESSION_SECRET environment variable is required")
    UPLOAD_FOLDER = 'static/images'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # ML Model configuration
    FEATURE_COLUMNS = [
        'luas_tanah', 'luas_bangunan', 'kamar_tidur', 'kamar_mandi', 
        'carport', 'tahun_dibangun', 'jarak_sekolah', 'jarak_rs', 
        'jarak_pasar', 'jenis_jalan_encoded', 'kondisi_encoded', 'sertifikat_encoded'
    ]
    
    # Gemini AI configuration
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    
    # Encoding mappings for categorical variables
    JENIS_JALAN_MAP = {'gang_kecil': 1, 'jalan_sedang': 2, 'jalan_besar': 3}
    KONDISI_MAP = {'butuh_renovasi': 1, 'renovasi_ringan': 2, 'baik': 3, 'baru': 4}
    SERTIFIKAT_MAP = {'lainnya': 1, 'HGB': 2, 'SHM': 3}