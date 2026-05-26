# Section 3.4 — Machine Learning Model Development (Revised)

*Use this text to replace or expand Section 3.4 in your thesis. It addresses supervisor feedback on logistic regression equations and multiclass classification.*

---

## 3.4 Machine Learning Model Development

Four supervised machine learning algorithms were implemented and evaluated for cattle disease classification:

- Logistic Regression  
- Random Forest  
- Decision Tree  
- Support Vector Machine (SVM)

These algorithms were selected because they are widely used and well validated for classification problems, and they are appropriate for structured symptom-based datasets common in medical and agricultural decision-support systems. All models were implemented in Python using the **Scikit-learn** library.

### 3.4.1 Problem formulation

The prediction task is **multiclass classification**: each record must be assigned to **one of 26 cattle diseases** based on observed symptoms and contextual farm/animal attributes. The target variable (disease label) is encoded as integers \(0, 1, \ldots, 25\) using a `LabelEncoder`, while the input consists of a feature vector built from:

- **93 binary symptom indicators** (present = 1, absent = 0)  
- **9 contextual features** (e.g. age, sex, breed, vaccination status, herd size, farming type, movement history, season, province)

After preprocessing (scaling of numerical fields and one-hot encoding of categorical fields), the feature space expands from 102 raw columns to **113 model inputs**. This preprocessing pipeline is fitted on the training set only and reused at prediction time in the deployed Django application to prevent data leakage.

### 3.4.2 Logistic regression: equations and multiclass extension

Although the name contains “regression,” logistic regression is a **classification** method. It models the probability of class membership using a linear score passed through a sigmoid (binary case) or softmax (multiclass case).

#### Binary logistic regression

For two classes, the model estimates the probability of the positive class as:

\[
P(y = 1 \mid \mathbf{x}) = \sigma(\mathbf{w}^\top \mathbf{x} + b) = \frac{1}{1 + e^{-(\mathbf{w}^\top \mathbf{x} + b)}}
\]

where:

- \(\mathbf{x}\) is the feature vector (symptoms and encoded contextual features),  
- \(\mathbf{w}\) is the weight vector,  
- \(b\) is the bias term,  
- \(\sigma(\cdot)\) is the sigmoid function.

Training finds \(\mathbf{w}\) and \(b\) by minimizing the **log-loss** (cross-entropy) on the training data, optionally with **L2 regularization** to reduce overfitting:

\[
\mathcal{L}(\mathbf{w}, b) = -\sum_{i=1}^{N} \left[ y_i \log \hat{p}_i + (1 - y_i) \log (1 - \hat{p}_i) \right] + \frac{1}{2C} \|\mathbf{w}\|_2^2
\]

where \(\hat{p}_i = P(y_i = 1 \mid \mathbf{x}_i)\) and \(C\) controls regularization strength (smaller \(C\) implies stronger penalty on large weights).

#### Multinomial logistic regression (used in this system)

**Yes — logistic regression can be used for multiclass classification.** For \(K\) classes (in this project, \(K = 26\) diseases), **multinomial (softmax) logistic regression** assigns a score to each class \(k\) and normalizes scores into a probability distribution:

\[
z_k = \mathbf{w}_k^\top \mathbf{x} + b_k
\]

\[
P(y = k \mid \mathbf{x}) = \frac{e^{z_k}}{\sum_{j=1}^{K} e^{z_j}} \quad \text{for } k = 1, 2, \ldots, K
\]

The predicted disease is the class with the highest probability:

\[
\hat{y} = \arg\max_{k} \, P(y = k \mid \mathbf{x})
\]

This formulation is appropriate here because each case has **exactly one** true disease label among 26 mutually exclusive classes.

In Scikit-learn, multiclass logistic regression was configured as:

```python
LogisticRegression(
    max_iter=1000,
    random_state=42,
    solver='lbfgs',
    C=0.2,
    penalty='l2'
)
```

The **L-BFGS** solver fits the multinomial model for multi-class targets. Hyperparameters were chosen to balance accuracy and generalization: `C=0.2` applies moderate L2 regularization, and `max_iter=1000` ensures convergence.

### 3.4.3 Other algorithms (summary)

For comparison, three additional classifiers were trained on the same preprocessed feature vectors and encoded labels:

| Algorithm        | Role in this study |
|------------------|--------------------|
| **Decision Tree** | Non-linear, rule-based baseline; constrained depth to limit overfitting |
| **Random Forest** | Ensemble of trees; captures feature interactions |
| **SVM (RBF kernel)** | Non-linear boundary in high-dimensional space; probability estimates enabled for comparison |

Each model received identical train/test splits and evaluation metrics so that performance differences reflect algorithm choice rather than data handling.

### 3.4.4 Training, validation, and model selection

Models were trained on a stratified **80% training / 20% test** split so that all 26 disease classes were represented proportionally in both sets. **5-fold stratified cross-validation** on the training data was used to estimate generalization before final test evaluation.

Performance was measured using **accuracy**, **precision**, **recall**, and **F1-score** (weighted averages across classes to account for class imbalance). The best model was selected using accuracy in the target range (90–93%) combined with a low train–test gap (overfitting check).

**Results on the held-out test set:**

| Model                 | Test accuracy | Test F1 | Notes                          |
|-----------------------|---------------|---------|--------------------------------|
| **Logistic Regression** | **92.80%**    | **0.9282** | Selected as production model |
| SVM                   | 90.40%        | 0.9033  | Strong but higher overfitting gap |
| Random Forest         | 80.60%        | 0.7813  | Second among tree ensembles    |
| Decision Tree         | 34.70%        | 0.3344  | Limited by depth constraints   |

Logistic Regression achieved the highest accuracy and F1-score with a train–test gap of **4.17%**, indicating stable learning without severe overfitting. It was therefore saved as **`best_disease_model.pkl`** and integrated into the web system.

### 3.4.5 Deployment in the cattle disease prediction system

At runtime, the Django `ml_engine` service:

1. Builds a feature dictionary from farmer-entered symptoms and contextual inputs.  
2. Applies the saved **`preprocessor.pkl`** (same transformations as training).  
3. Calls **`predict`** and **`predict_proba`** on the saved logistic regression model.  
4. Maps the numeric class index back to a disease name using **`label_encoder.pkl`**.  
5. Returns the top predicted disease, confidence score, and the top three alternative diagnoses for transparency.

This end-to-end pipeline ensures that training-time preprocessing and multiclass probability outputs are used consistently in production predictions.

### 3.4.6 Summary

Feature vectors derived from symptom and contextual inputs allow the models to learn mappings from clinical signs to disease labels. **Multinomial logistic regression** was used explicitly for **26-class** disease classification, with formal binary and multiclass equations as shown above. Among the four algorithms evaluated, logistic regression provided the best balance of accuracy, stability, and deployability, and was adopted as the final model for the Early Disease Prediction for Cattle system.

---

## Short reply you can paste as a comment reply to your supervisor

> Thank you for the feedback. Section 3.4 has been updated to include the binary and multinomial (softmax) logistic regression equations. The system performs **multiclass classification** over **26 cattle diseases** using multinomial logistic regression in Scikit-learn (`solver='lbfgs'`, L2 regularization `C=0.2`). This model achieved **92.80% test accuracy** and was deployed as the production classifier in the Django application.
