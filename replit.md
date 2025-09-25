# Real Estate Price Recommendation System

## Overview

This is a Flask-based web application that provides real estate price recommendations using Machine Learning and AI integration. The system focuses on property price prediction for a specific area (kelurahan) and includes an AI chatbot powered by Gemini AI. Users can browse properties, get price predictions based on property characteristics, and interact with an AI assistant for property-related queries.

## Recent Development - September 25, 2025

✅ **Complete System Implementation**
- Core Flask Application with organized routing and error handling
- Property Management with full CRUD operations and JSON storage
- Machine Learning price prediction using RandomForest with automatic retraining
- Gemini AI Chatbot for natural language property queries
- Responsive Bootstrap frontend with property listings and search
- Google Maps integration with graceful fallbacks
- Advanced search and filtering by budget and property features
- Hidden admin panel at `/admin` for property management
- RESTful API endpoints for data access and predictions
- Workflow configured to run Flask server on port 5000

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Flask Framework**: Core web framework with organized folder structure
- **JSON File Storage**: Local data persistence using JSON files instead of traditional databases
- **Machine Learning Pipeline**: 
  - Uses scikit-learn RandomForestRegressor for price prediction
  - Features include property characteristics (size, rooms, location factors)
  - StandardScaler for feature normalization
  - Model persistence using pickle for trained models
- **RESTful API Design**: Clean endpoint structure for frontend communication
- **Session Management**: Flask sessions for user state management

### Frontend Architecture
- **Template Engine**: Jinja2 templating with Bootstrap 5 for responsive design
- **Component Structure**: 
  - Base template with shared navigation and styling
  - Specialized templates for different functionalities (admin, chat, properties, prediction)
- **Interactive Elements**: 
  - Property search and filtering
  - Real-time chat interface
  - Google Maps integration for location visualization
  - Image galleries with carousel functionality

### Data Storage Solutions
- **JSON-based Storage**: Property data stored in `data/properties.json`
- **File Upload System**: Property images stored in `static/images/` directory
- **Model Persistence**: Trained ML models saved in `models/` directory using pickle

### Authentication and Authorization
- **Admin Panel**: Hidden admin interface accessible via `/admin` URL
- **Session-based Security**: Uses Flask sessions with configurable secret key
- **File Upload Security**: Werkzeug secure_filename for safe file handling

### Machine Learning Architecture
- **Feature Engineering**: 
  - Property characteristics (land size, building size, rooms, etc.)
  - Location factors (distance to facilities, road type)
  - Condition and certificate encoding
- **Model Selection**: Random Forest Regressor for robust price prediction
- **Evaluation Metrics**: Mean Absolute Error and R² score for model performance
- **Preprocessing Pipeline**: Standard scaling for numerical features

## External Dependencies

### AI Integration
- **Gemini AI**: Google's Gemini 2.5-flash and 2.5-pro models for natural language processing
- **Google GenAI SDK**: Latest google-genai package for AI interactions
- **Structured Output**: Pydantic models for type-safe AI responses

### Maps and Location Services
- **Google Maps API**: 
  - JavaScript API for interactive map visualization
  - Geocoding for address to coordinates conversion
  - Distance calculation to nearby facilities

### Python Libraries
- **Data Processing**: pandas, numpy for data manipulation
- **Machine Learning**: scikit-learn for model training and prediction
- **Web Framework**: Flask with Werkzeug utilities
- **Environment Management**: python-dotenv for configuration

### Frontend Libraries
- **UI Framework**: Bootstrap 5.1.3 for responsive design
- **Icons**: Font Awesome 6.0.0 for consistent iconography
- **Styling**: Custom CSS with gradient backgrounds and smooth transitions

### Configuration Management
- **Environment Variables**: 
  - `GEMINI_API_KEY` for AI integration
  - `GOOGLE_MAPS_API_KEY` for maps functionality
  - `SESSION_SECRET` for secure sessions
- **File Upload Limits**: 16MB maximum file size for property images
- **Directory Structure**: Automatic creation of required directories (data, models, static/images)