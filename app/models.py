import json
import os
from typing import List, Dict, Optional
from app.config import Config

class PropertyRepository:
    """Handle property data operations"""
    
    @staticmethod
    def load_properties() -> List[Dict]:
        """Load properties from JSON file"""
        try:
            with open('data/properties.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    @staticmethod
    def save_properties(properties: List[Dict]) -> None:
        """Save properties to JSON file"""
        with open('data/properties.json', 'w') as f:
            json.dump(properties, f, indent=2)
    
    @staticmethod
    def get_property_by_id(property_id: str) -> Optional[Dict]:
        """Get property by ID"""
        properties = PropertyRepository.load_properties()
        return next((p for p in properties if p['id'] == property_id), None)
    
    @staticmethod
    def add_property(property_data: Dict) -> None:
        """Add new property"""
        properties = PropertyRepository.load_properties()
        properties.append(property_data)
        PropertyRepository.save_properties(properties)
    
    @staticmethod
    def delete_property(property_id: str) -> bool:
        """Delete property by ID"""
        properties = PropertyRepository.load_properties()
        original_count = len(properties)
        properties = [p for p in properties if p['id'] != property_id]
        
        if len(properties) < original_count:
            PropertyRepository.save_properties(properties)
            return True
        return False

def encode_categorical(value: str, mapping: Dict[str, int]) -> int:
    """Encode categorical values using provided mapping"""
    return mapping.get(value, 0)