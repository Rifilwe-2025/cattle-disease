import joblib

# Load feature names
features = joblib.load('feature_names.pkl')

# Filter out contextual features and one-hot encoded features
contextual = ['age_years', 'sex', 'breed', 'vaccinated', 'herd_size', 'farming_type', 'recent_movement', 'season', 'province']
prefixes = ['sex_', 'breed_', 'vaccinated_', 'farming_type_', 'recent_movement_', 'season_', 'province_']

symptoms = [f for f in features if f not in contextual and not any(f.startswith(p) for p in prefixes)]

print(f"Total features in model: {len(features)}")
print(f"Total symptoms: {len(symptoms)}")
print("\n" + "=" * 60)
print("ALL SYMPTOMS:")
print("=" * 60)
for i, s in enumerate(symptoms, 1):
    print(f"{i:3d}. {s}")
