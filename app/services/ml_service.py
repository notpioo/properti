import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import pickle
from typing import Optional, Dict, Any
from app.models import PropertyRepository, encode_categorical
from app.config import Config

class MLPredictionService:
    """Machine Learning service for property price prediction"""
    
    def __init__(self):
        self.model: Optional[RandomForestRegressor] = None
        self.scaler: Optional[StandardScaler] = None
        self.feature_columns = Config.FEATURE_COLUMNS
    
    def prepare_ml_data(self) -> Optional[pd.DataFrame]:
        """Prepare data for machine learning"""
        properties = PropertyRepository.load_properties()
        if len(properties) < 5:  # Need minimum data for training
            return None
        
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
                    encode_categorical(prop.get('jenis_jalan'), Config.JENIS_JALAN_MAP),
                    encode_categorical(prop.get('kondisi'), Config.KONDISI_MAP),
                    encode_categorical(prop.get('sertifikat'), Config.SERTIFIKAT_MAP),
                    float(prop['harga'])
                ]
                data.append(row)
        
        if len(data) < 5:
            return None
            
        columns = self.feature_columns + ['harga']
        df = pd.DataFrame(data, columns=columns)
        return df
    
    def train_model(self) -> bool:
        """Train the machine learning model"""
        df = self.prepare_ml_data()
        if df is None:
            return False
        
        # Prepare features and target
        X = df[self.feature_columns]
        y = df['harga']
        
        # Scale features
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model.fit(X_scaled, y)
        
        # Save model
        try:
            with open('models/price_model.pkl', 'wb') as f:
                pickle.dump({'model': self.model, 'scaler': self.scaler}, f)
            return True
        except Exception as e:
            print(f"Error saving model: {e}")
            return False
    
    def load_model(self) -> bool:
        """Load the trained ML model"""
        try:
            with open('models/price_model.pkl', 'rb') as f:
                model_data = pickle.load(f)
                self.model = model_data['model']
                self.scaler = model_data['scaler']
            return True
        except FileNotFoundError:
            return self.train_model()
        except Exception as e:
            print(f"Error loading model: {e}")
            return False
    
    def predict_price(self, property_data: Dict[str, Any]) -> Optional[float]:
        """Predict house price using ML model"""
        if self.model is None:
            if not self.load_model():
                return None
        
        # Prepare input data
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
            encode_categorical(property_data.get('jenis_jalan'), Config.JENIS_JALAN_MAP),
            encode_categorical(property_data.get('kondisi'), Config.KONDISI_MAP),
            encode_categorical(property_data.get('sertifikat'), Config.SERTIFIKAT_MAP)
        ]
        
        # Scale and predict
        if self.scaler is not None and self.model is not None:
            try:
                features_scaled = self.scaler.transform([features])
                prediction = self.model.predict(features_scaled)[0]
                return max(0, prediction)  # Ensure non-negative price
            except Exception as e:
                print(f"Error predicting price: {e}")
                return None
        
        return None

# Global ML service instance
ml_service = MLPredictionService()