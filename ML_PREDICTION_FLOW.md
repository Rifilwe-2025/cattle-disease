# ML Disease Prediction Flow - Visual Guide

## 🔄 Complete System Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                        FARMER REGISTERS                              │
│  (username, password, location, cattle info)                        │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         FARMER LOGS IN                               │
│  (authenticate with username & password)                            │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      FARMER DASHBOARD                                │
│  • View statistics (total/active/resolved cases)                    │
│  • View recent cases                                                │
│  • [Submit New Case] button ← Click here                           │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    SYMPTOM SELECTION FORM                            │
│  URL: /farmers/submit-case/                                         │
│                                                                      │
│  ☐ cough            ☐ fever            ☐ nasal_discharge          │
│  ☐ diarrhea         ☐ loss_appetite    ☐ weight_loss              │
│  ☐ lameness         ☐ swelling         ☐ skin_lesions             │
│  ☐ difficulty_breathing  ☐ eye_discharge  ☐ ...                   │
│                                                                      │
│  Additional Notes: [text area]                                      │
│                                                                      │
│  [Submit Case] ← Click to predict                                   │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    BACKEND PROCESSING                                │
│  farmers/views.py → submit_case()                                   │
│                                                                      │
│  1. Collect symptoms: ['cough', 'fever', 'nasal_discharge']        │
│                                                                      │
│  2. Call ML Engine:                                                 │
│     from ml_engine.services import predict_disease                  │
│     result = predict_disease(symptoms)                              │
│                                                                      │
│  3. ML Model Prediction:                                            │
│     ┌──────────────────────────────────────────┐                   │
│     │  Load model: best_disease_model.pkl     │                   │
│     │  Load encoder: label_encoder.pkl         │                   │
│     │  Load features: feature_names.pkl        │                   │
│     │                                           │                   │
│     │  • Convert symptoms to feature vector    │                   │
│     │  • Run prediction algorithm               │                   │
│     │  • Calculate confidence score             │                   │
│     │  • Decode disease name                    │                   │
│     └──────────────────────────────────────────┘                   │
│                                                                      │
│  4. Result:                                                         │
│     {                                                               │
│       'disease': 'Bovine Respiratory Disease',                     │
│       'confidence': 0.92                                            │
│     }                                                               │
│                                                                      │
│  5. Classify Severity:                                              │
│     severity = classify_severity(0.92, disease)                     │
│     → 'NON_SEVERE' (confidence ≥ 0.7)                              │
│                                                                      │
│  6. Save to Database:                                               │
│     Case.objects.create(                                            │
│       farmer=farmer,                                                │
│       symptoms=['cough', 'fever', ...],                            │
│       predicted_disease='Bovine Respiratory Disease',              │
│       confidence_score=0.92,                                        │
│       severity='NON_SEVERE',                                        │
│       status='PENDING'                                              │
│     )                                                               │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     SEVERITY-BASED ROUTING                           │
│                                                                      │
│  IF severity == 'NON_SEVERE' (Confidence ≥ 70%)                    │
│     → Show treatment recommendations                                │
│     → No vet needed                                                 │
│                                                                      │
│  ELIF severity == 'SEVERE' (50% ≤ Confidence < 70%)                │
│     → Redirect to vet selection page                                │
│     → Farmer chooses from nearby vets                               │
│                                                                      │
│  ELSE severity == 'CRITICAL' (Confidence < 50%)                     │
│     → Auto-assign nearest vet                                       │
│     → Send emergency notification                                   │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       RESULTS PAGE                                   │
│  URL: /farmers/case-result/<case_id>/                              │
│                                                                      │
│  ┌────────────────────────────────────────────────────┐            │
│  │ 📊 PREDICTION RESULTS                              │            │
│  ├────────────────────────────────────────────────────┤            │
│  │                                                     │            │
│  │  Predicted Disease:                                │            │
│  │  🐄 Bovine Respiratory Disease                    │            │
│  │                                                     │            │
│  │  Confidence Score:                                 │            │
│  │  ████████████████████░░ 92%                       │            │
│  │                                                     │            │
│  │  Severity: 🟢 NON-SEVERE                          │            │
│  │                                                     │            │
│  │  📋 Treatment Recommendations:                     │            │
│  │  • Isolate affected cattle from herd              │            │
│  │  • Follow standard treatment protocol              │            │
│  │  • Monitor closely for 48 hours                    │            │
│  │  • Contact vet if condition worsens                │            │
│  │                                                     │            │
│  │  [Back to Dashboard]                               │            │
│  └────────────────────────────────────────────────────┘            │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Key Components

### **1. Frontend (Web Interface)**
- **Technology**: Django Templates, HTML, CSS, Bootstrap
- **Files**: 
  - `templates/farmers/submit_case.html` - Symptom form
  - `templates/farmers/case_result.html` - Results display
  - `templates/farmers/dashboard.html` - Main dashboard

### **2. Backend (Django Views)**
- **Technology**: Python Django
- **File**: `farmers/views.py`
- **Functions**:
  - `submit_case()` - Handle symptom submission
  - `case_result()` - Display prediction results
  - `select_vet()` - Vet selection for severe cases

### **3. ML Engine (Prediction Service)**
- **Technology**: scikit-learn, joblib, NumPy
- **File**: `ml_engine/services.py`
- **Functions**:
  - `predict_disease()` - Main prediction function
  - `classify_severity()` - Severity classification
  - `get_treatment_recommendations()` - Treatment advice

### **4. ML Models (Trained Files)**
- **Files**:
  - `best_disease_model.pkl` - Trained ML model (Random Forest/SVM/etc.)
  - `label_encoder.pkl` - Disease name encoder/decoder
  - `feature_names.pkl` - List of all 132 symptoms

### **5. Database (PostgreSQL/SQLite)**
- **Models**:
  - `User` - User accounts (accounts/models.py)
  - `Farmer` - Farmer profiles (farmers/models.py)
  - `Case` - Disease cases (cases/models.py)
  - `Vet` - Vet profiles (vets/models.py)

---

## 📊 Data Flow

```
Symptom Selection
      ↓
   ['cough', 'fever', 'nasal_discharge']
      ↓
Feature Vector Conversion
      ↓
   [0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, ...]
   (132 features: 1 = symptom present, 0 = absent)
      ↓
ML Model Prediction
      ↓
   Disease Code: 42
      ↓
Label Decoder
      ↓
   'Bovine Respiratory Disease'
      ↓
Confidence Calculation
      ↓
   0.92 (92%)
      ↓
Severity Classification
      ↓
   'NON_SEVERE'
      ↓
Save to Database + Display Results
```

---

## 🧠 ML Model Decision Process

```
Input Symptoms:
['cough', 'fever', 'nasal_discharge', 'loss_of_appetite']

↓ Convert to Feature Vector

[0,1,0,0,1,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,...]
 │ │       │       │       │
 │ └─cough └─fever └─nasal └─loss_appetite
 └─(other symptoms not present)

↓ ML Model Processing

Random Forest / SVM / Decision Tree
├─ Tree 1: Bovine Respiratory Disease (95%)
├─ Tree 2: Bovine Respiratory Disease (91%)
├─ Tree 3: Pneumonia (88%)
├─ Tree 4: Bovine Respiratory Disease (94%)
└─ Tree 5: Bovine Respiratory Disease (92%)

↓ Aggregate Predictions

Disease Probabilities:
├─ Bovine Respiratory Disease: 0.92 (92%)
├─ Pneumonia: 0.05 (5%)
├─ Bronchitis: 0.02 (2%)
└─ Other: 0.01 (1%)

↓ Select Highest Probability

Predicted Disease: Bovine Respiratory Disease
Confidence: 0.92

↓ Severity Classification

IF confidence ≥ 0.7:
   severity = 'NON_SEVERE' ✓
ELIF confidence ≥ 0.5:
   severity = 'SEVERE'
ELSE:
   severity = 'CRITICAL'

↓ Final Result

{
  'disease': 'Bovine Respiratory Disease',
  'confidence': 0.92,
  'severity': 'NON_SEVERE'
}
```

---

## 🎨 UI Screenshots (Text Representation)

### **Dashboard**
```
╔════════════════════════════════════════════════════════════╗
║  Farmer Dashboard - Welcome, John Farmer!                 ║
╠════════════════════════════════════════════════════════════╣
║                                                            ║
║  📊 Statistics                                            ║
║  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   ║
║  │ Total Cases  │  │ Active Cases │  │ Resolved     │   ║
║  │     15       │  │      3       │  │     12       │   ║
║  └──────────────┘  └──────────────┘  └──────────────┘   ║
║                                                            ║
║  [➕ Submit New Case]                                     ║
║                                                            ║
║  📋 Recent Cases                                          ║
║  ┌────────────────────────────────────────────────────┐  ║
║  │ Case #15 - Bovine Respiratory Disease (NON_SEVERE)│  ║
║  │ 2 days ago                                         │  ║
║  ├────────────────────────────────────────────────────┤  ║
║  │ Case #14 - Mastitis (SEVERE) - Vet Assigned      │  ║
║  │ 5 days ago                                         │  ║
║  └────────────────────────────────────────────────────┘  ║
╚════════════════════════════════════════════════════════════╝
```

### **Symptom Form**
```
╔════════════════════════════════════════════════════════════╗
║  Submit Disease Case                                      ║
╠════════════════════════════════════════════════════════════╣
║                                                            ║
║  Select Symptoms:                                         ║
║                                                            ║
║  ☑ cough              ☑ fever              ☐ diarrhea    ║
║  ☑ nasal_discharge    ☐ eye_discharge     ☐ lameness     ║
║  ☑ loss_of_appetite   ☐ weight_loss       ☐ swelling     ║
║  ☐ skin_lesions       ☐ difficulty_breathing              ║
║                                                            ║
║  Additional Notes:                                        ║
║  ┌────────────────────────────────────────────────────┐  ║
║  │ Cattle has been coughing for 2 days, mild fever   │  ║
║  │                                                     │  ║
║  └────────────────────────────────────────────────────┘  ║
║                                                            ║
║  [Submit Case]                                            ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
```

### **Results Page**
```
╔════════════════════════════════════════════════════════════╗
║  Prediction Results                                       ║
╠════════════════════════════════════════════════════════════╣
║                                                            ║
║  Predicted Disease:                                       ║
║  🐄 Bovine Respiratory Disease                           ║
║                                                            ║
║  Confidence Score:                                        ║
║  ████████████████████░░ 92%                              ║
║                                                            ║
║  ┌────────────────────────────────────────────────────┐  ║
║  │ Severity: 🟢 NON-SEVERE                            │  ║
║  └────────────────────────────────────────────────────┘  ║
║                                                            ║
║  📋 Treatment Recommendations:                            ║
║  • Isolate affected cattle from the herd                 ║
║  • Follow standard treatment protocol                     ║
║  • Monitor cattle closely for 48 hours                    ║
║  • Contact a vet if condition worsens                     ║
║                                                            ║
║  [Back to Dashboard]  [View Case History]                ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
```

---

## 💡 Quick Test Instructions

1. **Start server**: `python manage.py runserver`
2. **Login**: Use your farmer credentials
3. **Submit case**: Click "Submit New Case"
4. **Select symptoms**: Check 3-4 symptoms
5. **Submit**: Click submit button
6. **View results**: See predicted disease instantly!

---

## ❓ FAQ

**Q: Is there a REST API?**
A: Currently web interface only. REST API can be added if needed.

**Q: Can I integrate this with a mobile app?**
A: Yes! We can add Django REST Framework for API endpoints.

**Q: How accurate is the ML model?**
A: Check `ml_model_training.ipynb` outputs for accuracy metrics.

**Q: Can I retrain the model?**
A: Yes! Run `jupyter notebook ml_model_training.ipynb` or `python train_models.py`

**Q: Where is the data stored?**
A: Currently SQLite (db.sqlite3), can switch to PostgreSQL.

**Q: Can vets see the predictions?**
A: Yes! Vets can view assigned cases in their dashboard.
