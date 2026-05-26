# Testing severity levels (NON_SEVERE, SEVERE, CRITICAL)

Severity is based on the model’s **confidence** (max probability for the predicted disease):

- **NON_SEVERE:** confidence ≥ 0.40  
- **SEVERE:** 0.22 ≤ confidence < 0.40  
- **CRITICAL:** confidence < 0.22  

Use the **exact symptom names** below when selecting symptoms in **Submit Case** (they match the dropdown options).

---

## 1. To try for **NON_SEVERE** (high confidence)

Use a **clear, classic set** for one disease so the model can be confident.

**Mastitis-like (udder-focused):**  
Select these symptoms:

- `udder_swelling`
- `udder_heat`
- `udder_redness`
- `udder_pain`
- `milk_clots`
- `reduction_milk_vields` (note: spelling “vields” as in the system)

**Foot rot–like (lameness + swelling):**

- `lameness`
- `swelling`
- `pain`
- `unwillingness_to_move`

**Wooden tongue–like:**

- `swollen_tongue`
- `painful_tongue`
- `salivation`
- `diffculty_breath` (exact name in system)

---

## 2. To try for **SEVERE** (medium confidence)

Use symptoms that could match **more than one disease**, so the model is less certain.

**Respiratory / fever (could be pneumonia, IBR, or other):**

- `fever`
- `coughing`
- `nasel_discharges`
- `rapid_breathing`
- `depression`
- `loss_of_appetite`

**Digestive (could be several conditions):**

- `diarrhoea`
- `stomach_pain`
- `reduced_rumination`
- `lethargy`
- `reduces_feed_intake`

---

## 3. To try for **CRITICAL** (low confidence)

Use **very few** or **generic** symptoms so the model stays uncertain.

**Minimal:**

- `fever`
- `lethargy`

**Very generic:**

- `depression`
- `loss_of_appetite`
- `weakness`

---

## Tips

- If the dropdown shows **display labels** (e.g. “Udder Swelling”) instead of raw names, the stored value is still the internal name (e.g. `udder_swelling`). Select by the label that corresponds to the names above.
- Your model was trained on 26 diseases; actual confidence values depend on the trained model. If you still get almost all CRITICAL, adjust **SEVERITY_THRESHOLDS** in `cattle_disease_system/settings.py` (e.g. lower **NON_SEVERE** and **SEVERE**).
- To see the **confidence** for each case, check the case result page or add a temporary print in `ml_engine/services.py` after `confidence = float(np.max(probabilities))`.
