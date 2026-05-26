"""
Cattle Disease Prediction - Machine Learning Model Training Script

This script trains and evaluates four machine learning algorithms:
1. Logistic Regression
2. Decision Tree
3. Random Forest
4. Support Vector Machine (SVM)

Run this script to train the models:
    python train_models.py
"""

# Import necessary libraries
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
import joblib
import warnings
warnings.filterwarnings('ignore')

print("=" * 70)
print("Cattle Disease Prediction - ML Model Training")
print("=" * 70)
print("\nLibraries imported successfully!")

# Step 1: Load and Explore the Dataset
print("\n" + "=" * 70)
print("Step 1: Loading Training Dataset")
print("=" * 70)

train_df = pd.read_csv('Training.csv')
print(f"\nTraining Dataset Shape: {train_df.shape}")
print(f"\nNumber of unique diseases: {train_df['prognosis'].nunique()}")
print(f"\nDisease classes: {sorted(train_df['prognosis'].unique())}")

# Check for missing values
print(f"\nMissing values: {train_df.isnull().sum().sum()}")

# Step 2: Data Preprocessing
print("\n" + "=" * 70)
print("Step 2: Data Preprocessing")
print("=" * 70)

# Separate features and target
X = train_df.drop('prognosis', axis=1)
y = train_df['prognosis']

print(f"\nFeatures shape: {X.shape}")
print(f"Target shape: {y.shape}")

# Encode target variable (disease names to numeric labels)
print("\nEncoding target variable...")
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

print(f"Number of classes: {len(label_encoder.classes_)}")

# Save the label encoder
joblib.dump(label_encoder, 'label_encoder.pkl')
print("[OK] Label encoder saved as 'label_encoder.pkl'")

# Split data into training and testing sets (80-20 split)
print("\nSplitting data into train/test sets...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
)

print(f"Training set size: {X_train.shape}")
print(f"Testing set size: {X_test.shape}")

# Step 3: Train Multiple ML Models
print("\n" + "=" * 70)
print("Step 3: Training ML Models")
print("=" * 70)

# Initialize models
models = {
    'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
    'Decision Tree': DecisionTreeClassifier(random_state=42, max_depth=20),
    'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42, max_depth=20),
    'SVM': SVC(kernel='rbf', random_state=42, probability=True)
}

# Dictionary to store results
results = {}

print("\nTraining models...")
print("-" * 70)

# Train each model and evaluate
for name, model in models.items():
    print(f"\nTraining {name}...")
    
    # Train the model
    model.fit(X_train, y_train)
    
    # Make predictions
    y_pred = model.predict(X_test)
    
    # Calculate metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
    recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
    f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
    
    # Store results
    results[name] = {
        'model': model,
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1_score': f1,
        'predictions': y_pred
    }
    
    print(f"  Accuracy:  {accuracy:.4f}")
    print(f"  Precision: {precision:.4f}")
    print(f"  Recall:    {recall:.4f}")
    print(f"  F1-Score:  {f1:.4f}")

# Step 4: Compare Model Performance
print("\n" + "=" * 70)
print("Step 4: Model Performance Comparison")
print("=" * 70)

# Create comparison DataFrame
comparison_df = pd.DataFrame({
    'Model': list(results.keys()),
    'Accuracy': [results[m]['accuracy'] for m in results.keys()],
    'Precision': [results[m]['precision'] for m in results.keys()],
    'Recall': [results[m]['recall'] for m in results.keys()],
    'F1-Score': [results[m]['f1_score'] for m in results.keys()]
})

print("\nModel Performance Comparison:")
print("-" * 70)
print(comparison_df.to_string(index=False))
print("-" * 70)

# Find best model based on F1-score
best_model_name = comparison_df.loc[comparison_df['F1-Score'].idxmax(), 'Model']
print(f"\n[OK] Best Model: {best_model_name}")
print(f"[OK] Best F1-Score: {comparison_df['F1-Score'].max():.4f}")

# Step 5: Save the Best Model
print("\n" + "=" * 70)
print("Step 5: Saving Best Model")
print("=" * 70)

best_model = results[best_model_name]['model']
joblib.dump(best_model, 'best_disease_model.pkl')

print(f"\n[OK] Best model ({best_model_name}) saved as 'best_disease_model.pkl'")

# Step 6: Save Feature Names
print("\n" + "=" * 70)
print("Step 6: Saving Feature Names")
print("=" * 70)

feature_names = X.columns.tolist()
joblib.dump(feature_names, 'feature_names.pkl')

print(f"[OK] Feature names saved as 'feature_names.pkl'")
print(f"  Total features: {len(feature_names)}")

# Step 7: Detailed Evaluation
print("\n" + "=" * 70)
print("Step 7: Detailed Evaluation of Best Model")
print("=" * 70)

y_pred_best = results[best_model_name]['predictions']
print(f"\nClassification Report for {best_model_name}:")
print("-" * 70)
print(classification_report(y_test, y_pred_best, target_names=label_encoder.classes_))

# Step 8: Test on External Testing Dataset (Optional)
print("\n" + "=" * 70)
print("Step 8: Testing on External Dataset")
print("=" * 70)

try:
    test_df = pd.read_csv('Testing.csv')
    print(f"\nTesting Dataset Shape: {test_df.shape}")
    
    X_test_external = test_df.drop('prognosis', axis=1)
    y_test_external = test_df['prognosis']
    y_test_external_encoded = label_encoder.transform(y_test_external)
    
    # Predict using best model
    y_pred_external = best_model.predict(X_test_external)
    
    # Calculate metrics
    accuracy_ext = accuracy_score(y_test_external_encoded, y_pred_external)
    precision_ext = precision_score(y_test_external_encoded, y_pred_external, average='weighted', zero_division=0)
    recall_ext = recall_score(y_test_external_encoded, y_pred_external, average='weighted', zero_division=0)
    f1_ext = f1_score(y_test_external_encoded, y_pred_external, average='weighted', zero_division=0)
    
    print(f"\nExternal Test Set Performance ({best_model_name}):")
    print(f"  Accuracy:  {accuracy_ext:.4f}")
    print(f"  Precision: {precision_ext:.4f}")
    print(f"  Recall:    {recall_ext:.4f}")
    print(f"  F1-Score:  {f1_ext:.4f}")
    
except Exception as e:
    print(f"\n[WARNING] Could not load Testing.csv: {e}")
    print("  Skipping external test set evaluation.")

# Summary
print("\n" + "=" * 70)
print("TRAINING COMPLETE!")
print("=" * 70)
print("\n[OK] Model files created:")
print("  1. best_disease_model.pkl - The trained ML model")
print("  2. label_encoder.pkl - Label encoder for disease names")
print("  3. feature_names.pkl - List of symptom features")
print("\n[OK] You can now use these models in the Django application!")
print("=" * 70)
