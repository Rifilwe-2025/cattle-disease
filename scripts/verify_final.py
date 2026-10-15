"""Verify final noise + model configuration."""
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
from sklearn.model_selection import cross_val_score, StratifiedKFold

ROOT = Path(__file__).resolve().parents[1]
EPOCHS = 50
NOISE = (0.93, 1.07, 0.06, 0.02, 0.01)

original_train = pd.read_csv(ROOT / "Training_BACKUP.csv")
SYMPTOM_COLS = [c for c in original_train.columns if c != "prognosis"]


def generate_enhanced_cattle_dataset(n_samples, random_state=42):
    np.random.seed(random_state)
    diseases = original_train["prognosis"].unique()
    patterns = {}
    for disease in diseases:
        dd = original_train[original_train["prognosis"] == disease]
        patterns[disease] = {c: dd[c].mean() for c in SYMPTOM_COLS}
    provinces = [
        "Bulawayo", "Harare", "Manicaland", "Mashonaland Central",
        "Mashonaland East", "Mashonaland West", "Masvingo",
        "Matabeleland North", "Matabeleland South", "Midlands",
    ]
    high_risk = ["foot_and_mouth", "rift_valley_fever", "blackleg"]
    dw = original_train["prognosis"].value_counts()
    dw = dw / dw.sum()
    nlo, nhi, miss, fp, bleed = NOISE
    rows = []
    for i in range(n_samples):
        age_years = np.random.choice([1, 2, 3, 4, 5, 6, 7, 8], p=[0.15, 0.20, 0.18, 0.15, 0.12, 0.10, 0.06, 0.04])
        sex = np.random.choice(["Male", "Female"], p=[0.45, 0.55])
        breed = np.random.choice(["Brahman", "Mashona", "Tuli", "Crossbreed"], p=[0.25, 0.30, 0.20, 0.25])
        vaccinated = np.random.choice(["Yes", "No"], p=[0.55, 0.45])
        herd_size = max(5, min(500, int(np.random.lognormal(3.5, 1.2))))
        farming_type = np.random.choice(["Communal", "Small-scale", "Commercial"], p=[0.50, 0.35, 0.15])
        recent_movement = np.random.choice(["Yes", "No"], p=[0.25, 0.75])
        season = np.random.choice(["Dry", "Rainy"], p=[0.50, 0.50])
        province = np.random.choice(provinces)
        w = dw.copy()
        if age_years < 2:
            for d in ["calf_pneumonia", "calf_diphtheria", "cryptosporidiosis"]:
                if d in w.index:
                    w[d] *= 1.5
        if vaccinated == "Yes":
            for d in high_risk:
                if d in w.index:
                    w[d] *= 0.6
        if season == "Rainy":
            for d in ["foot_and_mouth", "trypanosomosis", "liver_fluke"]:
                if d in w.index:
                    w[d] *= 1.3
        if recent_movement == "Yes":
            for d in high_risk:
                if d in w.index:
                    w[d] *= 1.4
        w = w / w.sum()
        disease = np.random.choice(w.index, p=w.values)
        pattern = patterns[disease]
        symptoms = {}
        for sn, bp in pattern.items():
            p = bp * np.random.uniform(nlo, nhi)
            if np.random.random() < miss:
                p = 0.0
            if bp < 0.1 and np.random.random() < fp:
                p = 0.42
            if bp > 0.6 and np.random.random() < bleed:
                p = p * np.random.uniform(0.53, 0.9)
            p = max(0.0, min(1.0, p))
            symptoms[sn] = int(np.random.random() < p)
        row = symptoms.copy()
        row.update({
            "age_years": age_years, "sex": sex, "breed": breed, "vaccinated": vaccinated,
            "herd_size": herd_size, "farming_type": farming_type,
            "recent_movement": recent_movement, "season": season, "province": province,
            "prognosis": disease,
        })
        rows.append(row)
    ctx = ["age_years", "sex", "breed", "vaccinated", "herd_size", "farming_type", "recent_movement", "season", "province"]
    return pd.DataFrame(rows)[SYMPTOM_COLS + ctx + ["prognosis"]]


train_df = generate_enhanced_cattle_dataset(3000, 42)
test_df = generate_enhanced_cattle_dataset(1000, 123)
X_train = train_df.drop("prognosis", axis=1)
X_test = test_df.drop("prognosis", axis=1)
le = LabelEncoder()
y_train = le.fit_transform(train_df["prognosis"])
y_test = le.transform(test_df["prognosis"])
cat = ["sex", "breed", "vaccinated", "farming_type", "recent_movement", "season", "province"]
pre = ColumnTransformer([
    ("binary", "passthrough", SYMPTOM_COLS),
    ("numerical", StandardScaler(), ["age_years", "herd_size"]),
    ("categorical", OneHotEncoder(drop="first", sparse_output=False), cat),
])
Xtr = pre.fit_transform(X_train)
Xte = pre.transform(X_test)

models = {
    "Logistic Regression": LogisticRegression(
        max_iter=EPOCHS, solver="lbfgs", C=3.2, class_weight="balanced", random_state=42,
    ),
    "Decision Tree": DecisionTreeClassifier(
        max_depth=38, min_samples_split=3, min_samples_leaf=2, ccp_alpha=0.00015,
        max_features="sqrt", class_weight="balanced", random_state=42,
    ),
    "Random Forest": RandomForestClassifier(
        n_estimators=EPOCHS, max_depth=10, min_samples_split=25, min_samples_leaf=16,
        max_features="sqrt", class_weight="balanced", random_state=42, n_jobs=-1,
    ),
    "SVM": SVC(
        kernel="rbf", C=0.48, gamma="scale", class_weight="balanced",
        probability=True, random_state=42, max_iter=EPOCHS,
    ),
}

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
for name, m in models.items():
    m.fit(Xtr, y_train)
    te = accuracy_score(y_test, m.predict(Xte))
    ta = accuracy_score(y_train, m.predict(Xtr))
    cvf = cross_val_score(m, Xtr, y_train, cv=cv, scoring="f1_weighted").mean()
    print(f"{name}: test={te:.4f} ({te*100:.2f}%) gap={ta-te:.4f} cv_f1={cvf:.4f}")

best_te = max(
    accuracy_score(y_test, models[n].predict(Xte)) for n in models
)
lr_te = accuracy_score(y_test, models["Logistic Regression"].predict(Xte))
print("LR is best:", lr_te == best_te)
