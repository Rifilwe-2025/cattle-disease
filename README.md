# Early Disease Prediction and Veterinary Recommendation System for Cattle

## Project Overview

This is an academic capstone project that implements a comprehensive system for early disease prediction in cattle using machine learning. The system helps farmers detect diseases early, connects them with nearby veterinary doctors, and enables the Ministry of Agriculture to monitor disease outbreaks across Zimbabwe.

## Features

- **ML-Powered Disease Prediction**: Uses four machine learning algorithms (Logistic Regression, Decision Tree, Random Forest, SVM) to predict diseases from symptoms
- **Severity Classification**: Automatically classifies disease severity (Non-Severe, Severe, Critical)
- **Vet Recommendation System**: Automatically connects farmers with nearby vets based on severity and location
- **Disease Surveillance Maps**: Interactive maps and heatmaps for monitoring outbreaks
- **Role-Based Access**: Three user roles - Farmer, Vet Doctor, Ministry Admin

## Technology Stack

- **Backend**: Python Django
- **Database**: PostgreSQL (primary), SQLite3 (backup)
- **Machine Learning**: scikit-learn, pandas, numpy
- **Frontend**: Bootstrap 5, HTML5, CSS3, JavaScript
- **Maps**: Leaflet.js
- **ML Training**: Jupyter Notebook

## Project Structure

```
cattle_disease_system/
├── accounts/          # Authentication and user management
├── farmers/           # Farmer registration and case submission
├── vets/              # Vet application and case management
├── ministry/          # Ministry admin dashboard and analytics
├── cases/             # Disease case management
├── ml_engine/         # ML prediction services
├── maps/              # Maps and surveillance
├── landing/            # Public landing page
├── templates/          # HTML templates
├── static/             # CSS, JS, images
├── ml_model_training.ipynb  # ML model training notebook
├── Training.csv       # Training dataset
├── Testing.csv         # Testing dataset
└── manage.py
```

## Installation

1. **Clone the repository** (or extract the project files)

2. **Create and activate virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Train the ML model**:
   - Open `ml_model_training.ipynb` in Jupyter
   - Run all cells to train the models
   - This will generate:
     - `best_disease_model.pkl`
     - `label_encoder.pkl`
     - `feature_names.pkl`

5. **Set up database**:
   - For PostgreSQL (recommended):
     - Create a database named `cattle_disease_db`
     - Update database credentials in `settings.py`
   - For SQLite (fallback):
     - The system will automatically use SQLite if PostgreSQL is not available

6. **Run migrations**:
```bash
python manage.py makemigrations
python manage.py migrate
```

7. **Create superuser** (for Ministry admin):
```bash
python manage.py createsuperuser
```

8. **Run the development server**:
```bash
python manage.py runserver
```

## Usage

### For Farmers

1. Register at the landing page
2. Complete farmer profile with location and cattle details
3. Submit disease cases by selecting symptoms
4. View ML predictions and recommendations
5. Select or get auto-assigned vets for severe/critical cases

### For Vet Doctors

1. Apply for registration at the landing page
2. Wait for Ministry approval
3. Register login credentials after approval
4. View assigned cases in dashboard
5. Submit diagnosis and recommendations
6. Close resolved cases

### For Ministry Admin

1. Login with superuser credentials
2. Approve/reject vet applications
3. View analytics and disease statistics
4. Monitor disease maps and heatmaps
5. Generate reports

## ML Model Training

The system uses a Jupyter notebook (`ml_model_training.ipynb`) to train four ML algorithms:

1. **Logistic Regression**
2. **Decision Tree**
3. **Random Forest**
4. **Support Vector Machine (SVM)**

The best performing model (based on F1-score) is automatically selected and saved for use in the Django application.

## Disease Severity Logic

- **Non-Severe** (Confidence ≥ 0.7): Show treatment recommendations, no vet required
- **Severe** (0.5 ≤ Confidence < 0.7): Trigger nearby vets, farmer selects preferred vet
- **Critical** (Confidence < 0.5): Auto-assign nearest available vet immediately

## Geolocation & Distance Calculation

The system uses the Haversine formula to calculate distances between farmers and vets. Vets are ranked by proximity, and the nearest vet is automatically assigned for critical cases.

## Maps & Surveillance

- Province-level disease distribution maps
- Interactive heatmaps showing case density
- Filters by disease type, date range, and province
- Suitable for academic presentation and ministry monitoring

## Database Models

- **User**: Custom user model with role-based authentication
- **Farmer**: Farmer profiles with location and cattle details
- **VetApplication**: Vet application submissions
- **Vet**: Approved vet profiles
- **Case**: Disease cases with symptoms, predictions, and vet consultations

## Development Notes

- The system is designed for academic capstone presentation
- All code is well-documented with docstrings
- UI is modern and responsive using Bootstrap 5
- ML pipeline is clearly explained in the notebook
- Business logic is commented throughout

## Future Enhancements

- Real-time notifications
- Mobile app version
- Integration with veterinary databases
- Advanced analytics and reporting
- Multi-language support

## License

This project is developed for academic purposes.

## Contact

For questions or support, please contact the development team.

---

**Note**: This system is designed for academic presentation to the Ministry of Agriculture, Zimbabwe.
