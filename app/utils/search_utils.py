import re
from typing import Dict, List, Optional, Any

def extract_search_criteria(query: str) -> Dict[str, Any]:
    """
    Extract search criteria from query using deterministic rules
    Returns: Dict with extracted criteria
    """
    query_lower = query.lower()
    criteria = {}
    
    # Extract budget (exact match only)
    budget_patterns = [
        r'(\d+)\s*juta',  # "500 juta"
        r'budget\s*(\d+)',  # "budget 500"
        r'(\d+)\s*m',  # "500m"
    ]
    
    for pattern in budget_patterns:
        matches = re.findall(pattern, query_lower)
        if matches:
            budget = int(matches[0]) * 1000000
            criteria['budget'] = budget
            criteria['budget_range'] = (budget * 0.8, budget * 1.2)  # ±20%
            break
    
    # Extract bedroom count (exact match required)
    room_patterns = [
        r'(\d+)\s*kamar\s*tidur',  # "2 kamar tidur"
        r'(\d+)\s*kamar',          # "2 kamar"
        r'kamar\s*(\d+)',          # "kamar 2"
        r'(\d+)\s*bedroom',        # "2 bedroom"
    ]
    
    for pattern in room_patterns:
        matches = re.findall(pattern, query_lower)
        if matches:
            criteria['kamar_tidur'] = int(matches[0])
            break
    
    # Extract bathroom count
    bathroom_patterns = [
        r'(\d+)\s*kamar\s*mandi',  # "2 kamar mandi"
        r'(\d+)\s*bathroom',       # "2 bathroom"
    ]
    
    for pattern in bathroom_patterns:
        matches = re.findall(pattern, query_lower)
        if matches:
            criteria['kamar_mandi'] = int(matches[0])
            break
    
    # Extract location/facility requirements
    if any(term in query_lower for term in ['dekat sekolah', 'near school', 'sekolah']):
        criteria['max_distance_school'] = 500  # 500m
    
    if any(term in query_lower for term in ['dekat rumah sakit', 'dekat rs', 'near hospital', 'hospital']):
        criteria['max_distance_hospital'] = 1000  # 1km
    
    if any(term in query_lower for term in ['dekat pasar', 'near market', 'pasar']):
        criteria['max_distance_market'] = 800  # 800m
    
    # Extract condition preferences
    if any(term in query_lower for term in ['baru', 'new']):
        criteria['kondisi'] = 'baru'
    elif any(term in query_lower for term in ['baik', 'good']):
        criteria['kondisi'] = 'baik'
    
    # Extract price preferences
    if any(term in query_lower for term in ['murah', 'cheap', 'ekonomis']):
        criteria['price_preference'] = 'low'
    elif any(term in query_lower for term in ['mahal', 'expensive', 'mewah', 'luxury']):
        criteria['price_preference'] = 'high'
    
    # Extract size preferences
    if any(term in query_lower for term in ['besar', 'luas', 'big', 'large']):
        criteria['size_preference'] = 'large'
    elif any(term in query_lower for term in ['kecil', 'small', 'compact']):
        criteria['size_preference'] = 'small'
    
    return criteria

def filter_properties_strict(properties: List[Dict], criteria: Dict[str, Any]) -> List[Dict]:
    """
    Apply strict deterministic filtering based on extracted criteria
    """
    if not criteria:
        return properties
    
    filtered = []
    
    for prop in properties:
        matches = True
        
        # EXACT bedroom match (critical fix for the reported issue)
        if 'kamar_tidur' in criteria:
            prop_rooms = prop.get('kamar_tidur', 0)
            required_rooms = criteria['kamar_tidur']
            # For "2 kamar tidur" query, only show properties with EXACTLY 2 bedrooms
            if prop_rooms != required_rooms:
                matches = False
        
        # EXACT bathroom match
        if 'kamar_mandi' in criteria:
            prop_bathrooms = prop.get('kamar_mandi', 0)
            required_bathrooms = criteria['kamar_mandi']
            if prop_bathrooms != required_bathrooms:
                matches = False
        
        # Budget range filtering
        if 'budget_range' in criteria:
            prop_price = prop.get('harga', 0)
            if prop_price == 0:  # Skip properties without price
                matches = False
            else:
                min_budget, max_budget = criteria['budget_range']
                if not (min_budget <= prop_price <= max_budget):
                    matches = False
        
        # Distance filtering (strict)
        if 'max_distance_school' in criteria:
            if prop.get('jarak_sekolah', 9999) > criteria['max_distance_school']:
                matches = False
        
        if 'max_distance_hospital' in criteria:
            if prop.get('jarak_rs', 9999) > criteria['max_distance_hospital']:
                matches = False
        
        if 'max_distance_market' in criteria:
            if prop.get('jarak_pasar', 9999) > criteria['max_distance_market']:
                matches = False
        
        # Condition filtering
        if 'kondisi' in criteria:
            if prop.get('kondisi', '') != criteria['kondisi']:
                matches = False
        
        if matches:
            filtered.append(prop)
    
    # Apply preference-based sorting
    if 'price_preference' in criteria:
        if criteria['price_preference'] == 'low':
            filtered.sort(key=lambda p: p.get('harga', float('inf')))
        elif criteria['price_preference'] == 'high':
            filtered.sort(key=lambda p: p.get('harga', 0), reverse=True)
    
    if 'size_preference' in criteria:
        if criteria['size_preference'] == 'large':
            filtered.sort(key=lambda p: p.get('luas_tanah', 0) + p.get('luas_bangunan', 0), reverse=True)
        elif criteria['size_preference'] == 'small':
            filtered.sort(key=lambda p: p.get('luas_tanah', 0) + p.get('luas_bangunan', 0))
    
    return filtered

def is_property_related_query(query: str) -> bool:
    """Check if query contains property-related keywords"""
    property_keywords = [
        'rumah', 'juta', 'kamar', 'budget', 'luas', 'sekolah', 'hospital', 'pasar', 
        'properti', 'beli', 'cari', 'house', 'bedroom', 'bathroom', 'price', 'search'
    ]
    query_lower = query.lower()
    return any(keyword in query_lower for keyword in property_keywords)