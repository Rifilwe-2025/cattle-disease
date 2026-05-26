"""
Machine Learning prediction services.

This module handles disease prediction using the trained ML model
with proper preprocessing for all 113 features (93 symptoms + 9 contextual).
"""
import joblib
import numpy as np
import pandas as pd
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def load_model():
    """
    Load the trained ML model.
    Returns the model object.
    """
    try:
        model = joblib.load(settings.ML_MODEL_PATH)
        return model
    except FileNotFoundError:
        raise ImproperlyConfigured(
            "ML model file not found. Please run the training notebook first."
        )


def load_label_encoder():
    """
    Load the label encoder for disease names.
    Returns the label encoder object.
    """
    try:
        encoder = joblib.load(settings.LABEL_ENCODER_PATH)
        return encoder
    except FileNotFoundError:
        raise ImproperlyConfigured(
            "Label encoder file not found. Please run the training notebook first."
        )


def load_preprocessor():
    """
    Load the feature preprocessor (StandardScaler + OneHotEncoder).
    Returns the preprocessor object.
    """
    try:
        preprocessor = joblib.load(settings.PREPROCESSOR_PATH)
        return preprocessor
    except FileNotFoundError:
        raise ImproperlyConfigured(
            "Preprocessor file not found. Please run the training notebook first."
        )


def load_feature_names():
    """
    Load the feature names (symptoms) from the trained model.
    Returns a list of feature names.
    """
    try:
        features = joblib.load(settings.FEATURE_NAMES_PATH)
        return features
    except FileNotFoundError:
        raise ImproperlyConfigured(
            "Feature names file not found. Please run the training notebook first."
        )


def predict_disease(symptoms, contextual_features):
    """
    Predict disease based on symptoms and contextual features.
    
    Args:
        symptoms: List of symptom names (e.g., ['fever', 'coughing'])
        contextual_features: Dict with contextual info:
            {
                'age_years': int (1-8),
                'sex': str ('Male' or 'Female'),
                'breed': str ('Brahman', 'Mashona', 'Tuli', 'Crossbreed'),
                'vaccinated': str ('Yes' or 'No'),
                'herd_size': int (5-500),
                'farming_type': str ('Communal', 'Small-scale', 'Commercial'),
                'recent_movement': str ('Yes' or 'No'),
                'season': str ('Dry' or 'Rainy'),
                'province': str (Zimbabwe province name)
            }
        
    Returns:
        dict with 'disease' (str), 'confidence' (float), and 'probabilities' (dict)
    """
    try:
        model = load_model()
        label_encoder = load_label_encoder()
        preprocessor = load_preprocessor()
        
        # Define all 93 symptom columns (must match training order)
        SYMPTOM_COLS = [
            'anorexia', 'abdominal_pain', 'anaemia', 'abortions', 'acetone',
            'aggression', 'arthrogyposis', 'ankylosis', 'anxiety', 'bellowing',
            'blood_loss', 'blood_poisoning', 'blisters', 'colic', 'Condemnation_of_livers',
            'conjunctivae', 'coughing', 'depression', 'discomfort', 'dyspnea',
            'dysentery', 'diarrhoea', 'dehydration', 'drooling', 'dull',
            'decreased_fertility', 'diffculty_breath', 'emaciation', 'encephalitis', 'fever',
            'facial_paralysis', 'frothing_of_mouth', 'frothing', 'gaseous_stomach', 'highly_diarrhoea',
            'high_pulse_rate', 'high_temp', 'high_proportion', 'hyperaemia', 'hydrocephalus',
            'isolation_from_herd', 'infertility', 'intermittent_fever', 'jaundice', 'ketosis',
            'loss_of_appetite', 'lameness', 'lack_of-coordination', 'lethargy', 'lacrimation',
            'milk_flakes', 'milk_watery', 'milk_clots', 'mild_diarrhoea', 'moaning',
            'mucosal_lesions', 'milk_fever', 'nausea', 'nasel_discharges', 'oedema',
            'pain', 'painful_tongue', 'pneumonia', 'photo_sensitization', 'quivering_lips',
            'reduction_milk_vields', 'rapid_breathing', 'rumenstasis', 'reduced_rumination', 'reduced_fertility',
            'reduced_fat', 'reduces_feed_intake', 'raised_breathing', 'stomach_pain', 'salivation',
            'stillbirths', 'shallow_breathing', 'swollen_pharyngeal', 'swelling', 'saliva',
            'swollen_tongue', 'tachycardia', 'torticollis', 'udder_swelling', 'udder_heat',
            'udder_hardeness', 'udder_redness', 'udder_pain', 'unwillingness_to_move', 'ulcers',
            'vomiting', 'weight_loss', 'weakness'
        ]
        
        # STEP 1: Create symptom vector (93 binary features)
        symptom_vector = {}
        for symptom in SYMPTOM_COLS:
            symptom_vector[symptom] = 1 if symptom in symptoms else 0
        
        # STEP 2: Add contextual features (9 features)
        # Provide defaults if not given
        contextual_data = {
            'age_years': contextual_features.get('age_years', 3),
            'sex': contextual_features.get('sex', 'Female'),
            'breed': contextual_features.get('breed', 'Crossbreed'),
            'vaccinated': contextual_features.get('vaccinated', 'No'),
            'herd_size': contextual_features.get('herd_size', 20),
            'farming_type': contextual_features.get('farming_type', 'Small-scale'),
            'recent_movement': contextual_features.get('recent_movement', 'No'),
            'season': contextual_features.get('season', 'Dry'),
            'province': contextual_features.get('province', 'Harare')
        }
        
        # STEP 3: Combine into single feature dict (102 total)
        feature_dict = {**symptom_vector, **contextual_data}
        
        # STEP 4: Convert to DataFrame (required for preprocessor)
        feature_df = pd.DataFrame([feature_dict])
        
        # STEP 5: Apply preprocessing (StandardScaler + OneHotEncoder)
        # This transforms 102 features → 113 features
        feature_vector = preprocessor.transform(feature_df)
        
        # STEP 6: Make prediction
        prediction = model.predict(feature_vector)[0]
        probabilities = model.predict_proba(feature_vector)[0]
        confidence = float(np.max(probabilities))
        
        # STEP 7: Decode disease name
        disease_name = label_encoder.inverse_transform([prediction])[0]
        
        probs_dict = dict(zip(label_encoder.classes_, probabilities.tolist()))
        # Top 3 diseases by probability (for low-confidence display)
        sorted_diseases = sorted(probs_dict.items(), key=lambda x: -x[1])[:3]
        top_3 = [{'disease': d, 'probability': round(float(p), 4)} for d, p in sorted_diseases]

        return {
            'disease': disease_name,
            'confidence': confidence,
            'probabilities': probs_dict,
            'top_3_diseases': top_3,
        }
    
    except Exception as e:
        # Fallback for development/testing
        return {
            'disease': 'Unknown',
            'confidence': 0.0,
            'probabilities': {},
            'top_3_diseases': [],
            'error': str(e)
        }


def classify_severity(confidence, disease_name=None):
    """
    Classify severity by disease danger first; use confidence to escalate when uncertain.
    
    - Base severity comes from DISEASE_SEVERITY (disease nature: CRITICAL/SEVERE/NON_SEVERE).
    - If confidence is low (below NON_SEVERE threshold), escalate: at least SEVERE so vet is always involved.
    
    Returns:
        str: 'NON_SEVERE', 'SEVERE', or 'CRITICAL'
    """
    thresholds = settings.SEVERITY_THRESHOLDS
    disease_severity_map = getattr(settings, 'DISEASE_SEVERITY', {})
    low_confidence_threshold = thresholds.get('NON_SEVERE', 0.40)

    # Base severity from disease danger
    if disease_name and disease_name in disease_severity_map:
        base = disease_severity_map[disease_name]
    else:
        base = 'NON_SEVERE'

    # Safety rule: low confidence → escalate to at least SEVERE
    if confidence < low_confidence_threshold:
        if base == 'NON_SEVERE':
            return 'SEVERE'
        if base == 'SEVERE':
            return 'SEVERE'
        return 'CRITICAL'
    return base


def get_treatment_recommendations(disease_name, severity):
    """
    Get treatment recommendations based on disease and severity.
    
    Args:
        disease_name: Name of the predicted disease
        severity: Severity level
        
    Returns:
        dict with recommendations
    """
    recommendations = {
        'NON_SEVERE': {
            'action': 'Home Treatment',
            'quarantine': 'Isolate affected cattle from the herd',
            'treatment': f'Follow standard treatment protocol for {disease_name}',
            'monitoring': 'Monitor cattle closely for 48 hours',
            'vet_required': False
        },
        'SEVERE': {
            'action': 'Veterinary Consultation Required',
            'quarantine': 'Immediately isolate affected cattle',
            'treatment': 'Wait for veterinary diagnosis before treatment',
            'monitoring': 'Monitor closely and contact vet if condition worsens',
            'vet_required': True
        },
        'CRITICAL': {
            'action': 'Emergency Veterinary Attention Required',
            'quarantine': 'Immediately isolate affected cattle and implement biosecurity measures',
            'treatment': 'Do not attempt treatment - wait for emergency vet',
            'monitoring': 'Continuous monitoring required',
            'vet_required': True,
            'emergency': True
        }
    }
    
    base_recommendations = recommendations.get(severity, recommendations['SEVERE'])
    
    # Add disease-specific recommendations if available
    disease_specific = get_disease_specific_recommendations(disease_name)
    base_recommendations.update(disease_specific)
    
    return base_recommendations


def get_disease_specific_recommendations(disease_name):
    """
    Get disease-specific treatment recommendations.
    
    Args:
        disease_name: Name of the disease
        
    Returns:
        dict with disease-specific recommendations
    """
    # This can be expanded with a database or knowledge base
    disease_recommendations = {
        'mastitis': {
            'specific_treatment': 'Apply warm compresses, ensure proper milking hygiene',
            'medication': 'Antibiotics may be required - consult vet',
        },
        'foot_rot': {
            'specific_treatment': 'Clean and dry hooves, apply antiseptic',
            'medication': 'Antibiotic treatment recommended',
        },
        # Add more disease-specific recommendations as needed
    }
    
    return disease_recommendations.get(disease_name.lower(), {})
