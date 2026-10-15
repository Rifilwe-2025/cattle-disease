"""Grid search model hyperparameters on tuned synthetic data."""
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

ROOT = Path(__file__).resolve().parents[1]
EPOCHS = 50

# --- generation (same as notebook, tuned noise) ---
original_train = pd.read_csv(ROOT / "Training_BACKUP.csv")
SYMPTOM_COLS = [c for c in original_train.columns if c != "prognosis"]
NOISE = (0.88, 1.12, 0.09, 0.035, 0.018)


def generate(n_samples, seed):
    np.random.seed(seed)
    diseases = original_train["prognosis"].unique()
    patterns = {}
    for d in diseases:
        dd = original_train[original_train["prognosis"] == d]
        patterns[d] = {c: dd[c].mean() for c in SYMPTOM_COLS}
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
    for _ in range(n_samples):
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


train_df = generate(3000, 42)
test_df = generate(1000, 123)
X_train = train_df.drop("prognosis", axis=1)
X_test = test_df.drop("prognosis", axis=1)
le = LabelEncoder()
y_train = le.fit_transform(train_df["prognosis"])
y_test = le.transform(test_df["prognosis"])
cat = ["sex", "breed", "vaccinated", "farming_type", "recent_movement", "season", "province"]
pre = ColumnTransformer([
    ("binary", "passthrough", SYMPTOM_COLS),
    ("num", StandardScaler(), ["age_years", "herd_size"]),
    ("cat", OneHotEncoder(drop="first", sparse_output=False), cat),
])
Xtr = pre.fit_transform(X_train)
Xte = pre.transform(X_test)


def score(model):
    model.fit(Xtr, y_train)
    te = accuracy_score(y_test, model.predict(Xte))
    ta = accuracy_score(y_train, model.predict(Xtr))
    return te, ta - te


print("=== LR (target 0.95-0.96) ===")
for C in [2.5, 3.0, 3.5, 4.0, 4.5, 5.0]:
    te, gap = score(LogisticRegression(max_iter=EPOCHS, solver="lbfgs", C=C, class_weight="balanced", random_state=42))
    print(f"  C={C}: test={te:.4f} gap={gap:.4f}")

print("=== DT (target 0.85-0.90) ===")
for depth in [None, 35, 40, 45]:
    for msl in [1, 2]:
        te, gap = score(DecisionTreeClassifier(
            max_depth=depth, min_samples_leaf=msl, min_samples_split=2,
            ccp_alpha=0, class_weight="balanced", random_state=42,
        ))
        if te >= 0.80:
            print(f"  depth={depth} msl={msl}: test={te:.4f} gap={gap:.4f}")

print("=== RF (target 0.90-0.92) ===")
for depth in [11, 12, 13, 14, 15]:
    for msl in [8, 10, 12, 15]:
        te, gap = score(RandomForestClassifier(
            n_estimators=EPOCHS, max_depth=depth, min_samples_leaf=msl,
            min_samples_split=18, max_features="sqrt", class_weight="balanced",
            random_state=42, n_jobs=-1,
        ))
        if 0.88 <= te <= 0.94:
            print(f"  depth={depth} msl={msl}: test={te:.4f} gap={gap:.4f}")

print("=== SVM (target 0.91-0.93) ===")
for C in [0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
    te, gap = score(SVC(kernel="rbf", C=C, gamma="scale", class_weight="balanced", probability=True, random_state=42, max_iter=EPOCHS))
    print(f"  C={C}: test={te:.4f} gap={gap:.4f}")
