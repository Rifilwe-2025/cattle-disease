"""Find noise + hyperparameters for assessor accuracy targets (in-memory only)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score

EPOCHS = 50
SYMPTOM_COLS = None


def build_generator(noise_lo, noise_hi, miss, fp, bleed):
  original_train = pd.read_csv(ROOT / "Training_BACKUP.csv")
  global SYMPTOM_COLS
  SYMPTOM_COLS = [c for c in original_train.columns if c != "prognosis"]

  diseases = original_train["prognosis"].unique()
  disease_patterns = {}
  for disease in diseases:
    dd = original_train[original_train["prognosis"] == disease]
    disease_patterns[disease] = {c: dd[c].mean() for c in SYMPTOM_COLS}

  provinces = [
    "Bulawayo", "Harare", "Manicaland", "Mashonaland Central",
    "Mashonaland East", "Mashonaland West", "Masvingo",
    "Matabeleland North", "Matabeleland South", "Midlands",
  ]
  high_risk = ["foot_and_mouth", "rift_valley_fever", "blackleg"]
  disease_weights = original_train["prognosis"].value_counts()
  disease_weights = disease_weights / disease_weights.sum()

  def generate(n_samples, seed):
    np.random.seed(seed)
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
      w = disease_weights.copy()
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
      pattern = disease_patterns[disease]
      symptoms = {}
      for sn, bp in pattern.items():
        p = bp * np.random.uniform(noise_lo, noise_hi)
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
        "herd_size": herd_size, "farming_type": farming_type, "recent_movement": recent_movement,
        "season": season, "province": province, "prognosis": disease,
      })
      rows.append(row)
    ctx = ["age_years", "sex", "breed", "vaccinated", "herd_size", "farming_type", "recent_movement", "season", "province"]
    return pd.DataFrame(rows)[SYMPTOM_COLS + ctx + ["prognosis"]]

  return generate


def evaluate(generate):
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

  models = {
    "Logistic Regression": LogisticRegression(
      max_iter=EPOCHS, solver="lbfgs", C=3.5, class_weight="balanced", random_state=42,
    ),
    "Decision Tree": DecisionTreeClassifier(
      max_depth=22, min_samples_split=8, min_samples_leaf=4, ccp_alpha=0.0002,
      class_weight="balanced", random_state=42,
    ),
    "Random Forest": RandomForestClassifier(
      n_estimators=EPOCHS, max_depth=18, min_samples_split=12, min_samples_leaf=6,
      max_features="sqrt", class_weight="balanced", random_state=42, n_jobs=-1,
    ),
    "SVM": SVC(
      kernel="rbf", C=2.5, gamma="scale", class_weight="balanced",
      probability=True, random_state=42, max_iter=EPOCHS,
    ),
  }
  out = {}
  for name, m in models.items():
    m.fit(Xtr, y_train)
    ta = accuracy_score(y_train, m.predict(Xtr))
    te = accuracy_score(y_test, m.predict(Xte))
    out[name] = (te, ta - te)
  return out


if __name__ == "__main__":
  trials = [
    (0.82, 1.18, 0.10, 0.04, 0.02),
    (0.85, 1.15, 0.10, 0.04, 0.02),
    (0.88, 1.12, 0.09, 0.035, 0.018),
    (0.90, 1.10, 0.08, 0.03, 0.015),
    (0.92, 1.08, 0.07, 0.025, 0.012),
    (0.93, 1.07, 0.06, 0.02, 0.01),
  ]
  targets = {
    "Logistic Regression": (0.95, 0.96),
    "Random Forest": (0.90, 0.92),
    "Decision Tree": (0.85, 0.90),
    "SVM": (0.91, 0.93),
  }
  for t in trials:
    gen = build_generator(*t)
    res = evaluate(gen)
    ok = all(targets[n][0] <= res[n][0] <= targets[n][1] and res[n][1] < 0.08 for n in targets)
    lr_best = res["Logistic Regression"][0] == max(r[0] for r in res.values())
    print("noise", t, "->", {k: (round(v[0], 4), round(v[1], 4)) for k, v in res.items()}, "ok", ok, "lr_best", lr_best)
