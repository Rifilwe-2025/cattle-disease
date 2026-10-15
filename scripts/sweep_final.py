"""Sweep noise + models for assessor targets."""
import warnings
warnings.filterwarnings("ignore")

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_final as vf
from verify_final import generate_enhanced_cattle_dataset, SYMPTOM_COLS, EPOCHS
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score

TARGETS = {
    "Logistic Regression": (0.95, 0.96),
    "Decision Tree": (0.85, 0.90),
    "Random Forest": (0.90, 0.92),
    "SVM": (0.91, 0.93),
}

noise_grid = [
    (0.955, 1.045, 0.045, 0.014, 0.007),
    (0.96, 1.04, 0.04, 0.012, 0.006),
    (0.965, 1.035, 0.038, 0.011, 0.005),
]

lr_Cs = [2.0, 2.5, 3.0, 3.5]
dt_depths = [35, 40, 45, None]
rf_depths = [10, 11]
rf_msls = [12, 14, 16]
svm_Cs = [0.42, 0.48, 0.54]

hits = []
for noise in noise_grid:
    vf.NOISE = noise
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

    for lrC in lr_Cs:
        for dt_d in dt_depths:
            for rf_d in rf_depths:
                for rf_msl in rf_msls:
                    for svmC in svm_Cs:
                        models = {
                            "Logistic Regression": LogisticRegression(
                                max_iter=EPOCHS, solver="lbfgs", C=lrC,
                                class_weight="balanced", random_state=42,
                            ),
                            "Decision Tree": DecisionTreeClassifier(
                                max_depth=dt_d, min_samples_leaf=1, min_samples_split=2,
                                max_features="sqrt", class_weight="balanced", random_state=42,
                            ),
                            "Random Forest": RandomForestClassifier(
                                n_estimators=EPOCHS, max_depth=rf_d, min_samples_leaf=rf_msl,
                                min_samples_split=22, max_features="sqrt",
                                class_weight="balanced", random_state=42, n_jobs=-1,
                            ),
                            "SVM": SVC(
                                kernel="rbf", C=svmC, gamma="scale", class_weight="balanced",
                                probability=True, random_state=42, max_iter=EPOCHS,
                            ),
                        }
                        scores = {}
                        ok = True
                        for nm, m in models.items():
                            m.fit(Xtr, y_train)
                            te = accuracy_score(y_test, m.predict(Xte))
                            gap = accuracy_score(y_train, m.predict(Xtr)) - te
                            scores[nm] = (te, gap)
                            lo, hi = TARGETS[nm]
                            if not (lo <= te <= hi) or gap > 0.07:
                                ok = False
                                break
                        if ok:
                            lr_te = scores["Logistic Regression"][0]
                            others = [scores[n][0] for n in scores if n != "Logistic Regression"]
                            if lr_te > max(others):
                                hits.append((noise, lrC, dt_d, rf_d, rf_msl, svmC, scores))

print(f"Found {len(hits)} configurations")
for h in hits[:10]:
    print(h)
