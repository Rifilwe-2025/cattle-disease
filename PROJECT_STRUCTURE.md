# Project Structure Documentation

## Cattle Disease Prediction System - Project Structure

This document explains the structure and organization of the Cattle Disease Prediction System project.

## Directory Structure

```
cattle_disease_system/
│
├── accounts/              # Authentication and user management
│   ├── __init__.py
│   ├── models.py          # Custom User model with roles
│   ├── views.py           # Login, logout, redirect views
│   ├── forms.py           # Login and registration forms
│   ├── urls.py            # URL routing
│   ├── admin.py           # Admin configuration
│   └── apps.py
│
├── farmers/                # Farmer module
│   ├── __init__.py
│   ├── models.py          # Farmer profile model
│   ├── views.py           # Dashboard, case submission, vet selection
│   ├── forms.py           # Farmer registration and case forms
│   ├── urls.py            # URL routing
│   ├── admin.py           # Admin configuration
│   └── apps.py
│
├── vets/                   # Veterinary doctors module
│   ├── __init__.py
│   ├── models.py          # VetApplication and Vet models
│   ├── views.py           # Application, dashboard, case management
│   ├── forms.py           # Vet application and consultation forms
│   ├── utils.py           # Haversine distance calculation
│   ├── urls.py            # URL routing
│   ├── admin.py           # Admin configuration
│   └── apps.py
│
├── ministry/               # Ministry of Agriculture module
│   ├── __init__.py
│   ├── views.py           # Dashboard, vet approval, analytics
│   ├── urls.py            # URL routing
│   ├── admin.py           # Admin configuration
│   └── apps.py
│
├── cases/                  # Disease case management
│   ├── __init__.py
│   ├── models.py          # Case model
│   ├── urls.py            # URL routing (minimal)
│   ├── admin.py           # Admin configuration
│   └── apps.py
│
├── ml_engine/              # Machine Learning engine
│   ├── __init__.py
│   ├── services.py        # Prediction and severity classification
│   └── apps.py
│
├── maps/                   # Maps and surveillance
│   ├── __init__.py
│   ├── views.py           # Disease map and heatmap views
│   ├── urls.py            # URL routing
│   └── apps.py
│
├── landing/                # Public landing page
│   ├── __init__.py
│   ├── views.py           # Home page view
│   ├── urls.py            # URL routing
│   └── apps.py
│
├── templates/               # HTML templates
│   ├── base.html          # Base template
│   ├── landing/           # Landing page templates
│   ├── accounts/          # Authentication templates
│   ├── farmers/           # Farmer templates
│   ├── vets/              # Vet templates
│   ├── ministry/          # Ministry templates
│   └── maps/              # Map templates
│
├── static/                  # Static files
│   ├── css/               # Stylesheets
│   ├── js/                # JavaScript files
│   └── images/            # Images
│
├── cattle_disease_system/   # Main project configuration
│   ├── __init__.py
│   ├── settings.py        # Django settings
│   ├── urls.py            # Main URL configuration
│   ├── wsgi.py            # WSGI configuration
│   └── asgi.py            # ASGI configuration
│
├── ml_model_training.ipynb  # Jupyter notebook for ML training
├── Training.csv            # Training dataset
├── Testing.csv             # Testing dataset
├── manage.py               # Django management script
├── requirements.txt        # Python dependencies
├── README.md              # Project documentation
└── .gitignore             # Git ignore file
```

## App Responsibilities

### accounts/
- **Purpose**: User authentication and role management
- **Key Features**:
  - Custom User model with role field (FARMER, VET, MINISTRY)
  - Login/logout functionality
  - Role-based redirect after login

### farmers/
- **Purpose**: Farmer registration and case submission
- **Key Features**:
  - Farmer profile creation
  - Disease case submission with symptom selection
  - Case history viewing
  - Vet selection for severe cases

### vets/
- **Purpose**: Vet application and case management
- **Key Features**:
  - Vet application submission
  - Application approval workflow
  - Case assignment and consultation
  - Distance calculation using Haversine formula

### ministry/
- **Purpose**: Administrative oversight and monitoring
- **Key Features**:
  - Vet application approval/rejection
  - System-wide analytics
  - Disease statistics
  - Report generation

### cases/
- **Purpose**: Disease case data model
- **Key Features**:
  - Case model with symptoms, predictions, and vet consultations
  - Status tracking (PENDING, ASSIGNED, IN_PROGRESS, RESOLVED)
  - Severity classification

### ml_engine/
- **Purpose**: Machine learning prediction services
- **Key Features**:
  - Disease prediction from symptoms
  - Severity classification
  - Treatment recommendations
  - Model loading and inference

### maps/
- **Purpose**: Disease surveillance visualization
- **Key Features**:
  - Interactive disease distribution maps
  - Heatmaps for case density
  - Province-level filtering
  - Date range filtering

### landing/
- **Purpose**: Public-facing landing page
- **Key Features**:
  - System overview
  - Registration links
  - Feature highlights

## Data Flow

1. **Farmer Registration** → `accounts` → `farmers`
2. **Case Submission** → `farmers` → `ml_engine` → `cases`
3. **Vet Assignment** → `vets/utils` → `cases`
4. **Vet Consultation** → `vets` → `cases`
5. **Ministry Monitoring** → `ministry` → `maps` → `cases`

## Database Models

- **User**: Authentication and roles
- **Farmer**: Farmer profiles with location
- **VetApplication**: Vet application submissions
- **Vet**: Approved vet profiles
- **Case**: Disease cases with predictions and consultations

## ML Pipeline

1. Train models using `ml_model_training.ipynb`
2. Save best model as `best_disease_model.pkl`
3. Load model in `ml_engine/services.py`
4. Predict disease from symptoms
5. Classify severity
6. Trigger appropriate response (treatment/vet assignment)

## Security & Access Control

- Role-based authentication
- Permission checks in views
- Ministry-only access for sensitive operations
- Vet approval workflow prevents unauthorized access

## Future Enhancements

- Real-time notifications
- Mobile API endpoints
- Advanced analytics dashboard
- Export functionality for reports
- Multi-language support
