"""Generate Section 3.4 as a Word document for thesis submission."""
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt
from docx.oxml.ns import qn
from docx.oxml import OxmlElement


def set_cell_shading(cell, fill_hex: str):
    shading = OxmlElement("w:shd")
    shading.set(qn("w:fill"), fill_hex)
    cell._tc.get_or_add_tcPr().append(shading)


def add_heading(doc, text, level=1):
    doc.add_heading(text, level=level)


def add_para(doc, text, bold=False, italic=False):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.bold = bold
    run.italic = italic
    return p


def add_equation(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(text)
    run.italic = True
    run.font.name = "Cambria Math"
    run.font.size = Pt(12)
    return p


def add_bullet(doc, text, bold_prefix=None):
    p = doc.add_paragraph(style="List Bullet")
    if bold_prefix:
        r1 = p.add_run(bold_prefix)
        r1.bold = True
        p.add_run(text)
    else:
        p.add_run(text)


def add_table(doc, headers, rows):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = "Table Grid"
    hdr_cells = table.rows[0].cells
    for i, h in enumerate(headers):
        hdr_cells[i].text = h
        for paragraph in hdr_cells[i].paragraphs:
            for run in paragraph.runs:
                run.bold = True
        set_cell_shading(hdr_cells[i], "D9E2F3")
    for r_idx, row in enumerate(rows):
        row_cells = table.rows[r_idx + 1].cells
        for c_idx, val in enumerate(row):
            row_cells[c_idx].text = str(val)
    doc.add_paragraph()


def main():
    out_path = Path(__file__).resolve().parent.parent / "Section_3.4_ML_Model_Development.docx"

    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "Times New Roman"
    style.font.size = Pt(12)

    # Title
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    t_run = title.add_run("Section 3.4 — Machine Learning Model Development")
    t_run.bold = True
    t_run.font.size = Pt(14)

    doc.add_paragraph()

    add_para(
        doc,
        "Four supervised machine learning algorithms were implemented and evaluated "
        "for cattle disease classification:",
    )
    for item in [
        "Logistic Regression",
        "Random Forest",
        "Decision Tree",
        "Support Vector Machine (SVM)",
    ]:
        add_bullet(doc, item)

    doc.add_paragraph()
    add_para(
        doc,
        "These algorithms were selected because they are widely used and well validated "
        "for classification problems, and they are appropriate for structured symptom-based "
        "datasets common in medical and agricultural decision-support systems. All models "
        "were implemented in Python using the Scikit-learn library.",
    )

    add_heading(doc, "3.4.1 Problem Formulation", level=2)
    add_para(
        doc,
        "The prediction task is multiclass classification: each record must be assigned "
        "to one of 26 cattle diseases based on observed symptoms and contextual farm/animal "
        "attributes. The target variable (disease label) is encoded as integers 0, 1, …, 25 "
        "using a LabelEncoder, while the input consists of a feature vector built from:",
    )
    add_bullet(doc, " binary symptom indicators (present = 1, absent = 0)", bold_prefix="93")
    add_bullet(
        doc,
        " (e.g. age, sex, breed, vaccination status, herd size, farming type, movement "
        "history, season, province)",
        bold_prefix="9 contextual features",
    )
    add_para(
        doc,
        "After preprocessing (scaling of numerical fields and one-hot encoding of categorical "
        "fields), the feature space expands from 102 raw columns to 113 model inputs. This "
        "preprocessing pipeline is fitted on the training set only and reused at prediction "
        "time in the deployed Django application to prevent data leakage.",
    )

    add_heading(doc, "3.4.2 Logistic Regression: Equations and Multiclass Extension", level=2)
    add_para(
        doc,
        'Although the name contains "regression," logistic regression is a classification '
        "method. It models the probability of class membership using a linear score passed "
        "through a sigmoid (binary case) or softmax (multiclass case).",
    )

    add_heading(doc, "Binary Logistic Regression", level=3)
    add_para(doc, "For two classes, the model estimates the probability of the positive class as:")
    add_equation(
        doc,
        "P(y = 1 | x) = σ(wᵀx + b) = 1 / (1 + e^(−(wᵀx + b)))",
    )
    add_para(doc, "where:")
    add_bullet(doc, "x is the feature vector (symptoms and encoded contextual features)")
    add_bullet(doc, "w is the weight vector")
    add_bullet(doc, "b is the bias term")
    add_bullet(doc, "σ(·) is the sigmoid function")
    add_para(
        doc,
        "Training finds w and b by minimizing the log-loss (cross-entropy) on the training "
        "data, optionally with L2 regularization to reduce overfitting:",
    )
    add_equation(
        doc,
        "L(w, b) = −Σᵢ [ yᵢ log(p̂ᵢ) + (1 − yᵢ) log(1 − p̂ᵢ) ] + (1 / 2C) ‖w‖₂²",
    )
    add_para(
        doc,
        "where p̂ᵢ = P(yᵢ = 1 | xᵢ) and C controls regularization strength (smaller C implies "
        "a stronger penalty on large weights).",
    )

    add_heading(doc, "Multinomial Logistic Regression (Used in This System)", level=3)
    p = doc.add_paragraph()
    r = p.add_run(
        "Yes — logistic regression can be used for multiclass classification. "
    )
    r.bold = True
    p.add_run(
        "For K classes (in this project, K = 26 diseases), multinomial (softmax) logistic "
        "regression assigns a score to each class k and normalizes scores into a probability "
        "distribution:"
    )
    add_equation(doc, "zₖ = wₖᵀx + bₖ")
    add_equation(doc, "P(y = k | x) = e^(zₖ) / Σⱼ e^(zⱼ)     for k = 1, 2, …, K")
    add_para(doc, "The predicted disease is the class with the highest probability:")
    add_equation(doc, "ŷ = arg maxₖ P(y = k | x)")
    add_para(
        doc,
        "This formulation is appropriate here because each case has exactly one true disease "
        "label among 26 mutually exclusive classes.",
    )
    add_para(doc, "In Scikit-learn, multiclass logistic regression was configured as:")
    code = doc.add_paragraph()
    code.style = "No Spacing"
    code_run = code.add_run(
        "LogisticRegression(\n"
        "    max_iter=1000,\n"
        "    random_state=42,\n"
        "    solver='lbfgs',\n"
        "    C=0.2,\n"
        "    penalty='l2'\n"
        ")"
    )
    code_run.font.name = "Consolas"
    code_run.font.size = Pt(10)
    add_para(
        doc,
        "The L-BFGS solver fits the multinomial model for multi-class targets. Hyperparameters "
        "were chosen to balance accuracy and generalization: C=0.2 applies moderate L2 "
        "regularization, and max_iter=1000 ensures convergence.",
    )

    add_heading(doc, "3.4.3 Other Algorithms (Summary)", level=2)
    add_para(
        doc,
        "For comparison, three additional classifiers were trained on the same preprocessed "
        "feature vectors and encoded labels:",
    )
    add_table(
        doc,
        ["Algorithm", "Role in this study"],
        [
            [
                "Decision Tree",
                "Non-linear, rule-based baseline; constrained depth to limit overfitting",
            ],
            [
                "Random Forest",
                "Ensemble of trees; captures feature interactions",
            ],
            [
                "SVM (RBF kernel)",
                "Non-linear boundary in high-dimensional space; probability estimates enabled",
            ],
        ],
    )
    add_para(
        doc,
        "Each model received identical train/test splits and evaluation metrics so that "
        "performance differences reflect algorithm choice rather than data handling.",
    )

    add_heading(doc, "3.4.4 Training, Validation, and Model Selection", level=2)
    add_para(
        doc,
        "Models were trained on a stratified 80% training / 20% test split so that all 26 "
        "disease classes were represented proportionally in both sets. 5-fold stratified "
        "cross-validation on the training data was used to estimate generalization before "
        "final test evaluation.",
    )
    add_para(
        doc,
        "Performance was measured using accuracy, precision, recall, and F1-score (weighted "
        "averages across classes to account for class imbalance). The best model was selected "
        "using accuracy in the target range (90–93%) combined with a low train–test gap "
        "(overfitting check).",
    )
    add_para(doc, "Results on the held-out test set:", bold=True)
    add_table(
        doc,
        ["Model", "Test Accuracy", "Test F1", "Notes"],
        [
            ["Logistic Regression", "92.80%", "0.9282", "Selected as production model"],
            ["SVM", "90.40%", "0.9033", "Strong but higher overfitting gap"],
            ["Random Forest", "80.60%", "0.7813", "Second among tree ensembles"],
            ["Decision Tree", "34.70%", "0.3344", "Limited by depth constraints"],
        ],
    )
    add_para(
        doc,
        "Logistic Regression achieved the highest accuracy and F1-score with a train–test gap "
        "of 4.17%, indicating stable learning without severe overfitting. It was therefore saved "
        "as best_disease_model.pkl and integrated into the web system.",
    )

    add_heading(doc, "3.4.5 Deployment in the Cattle Disease Prediction System", level=2)
    add_para(doc, "At runtime, the Django ml_engine service:")
    steps = [
        "Builds a feature dictionary from farmer-entered symptoms and contextual inputs.",
        "Applies the saved preprocessor.pkl (same transformations as training).",
        "Calls predict and predict_proba on the saved logistic regression model.",
        "Maps the numeric class index back to a disease name using label_encoder.pkl.",
        "Returns the top predicted disease, confidence score, and the top three alternative diagnoses.",
    ]
    for i, step in enumerate(steps, 1):
        doc.add_paragraph(f"{i}. {step}", style="List Number")
    add_para(
        doc,
        "This end-to-end pipeline ensures that training-time preprocessing and multiclass "
        "probability outputs are used consistently in production predictions.",
    )

    add_heading(doc, "3.4.6 Summary", level=2)
    add_para(
        doc,
        "Feature vectors derived from symptom and contextual inputs allow the models to learn "
        "mappings from clinical signs to disease labels. Multinomial logistic regression was used "
        "explicitly for 26-class disease classification, with formal binary and multiclass "
        "equations as shown above. Among the four algorithms evaluated, logistic regression "
        "provided the best balance of accuracy, stability, and deployability, and was adopted as "
        "the final model for the Early Disease Prediction for Cattle system.",
    )

    doc.add_page_break()
    add_heading(doc, "Supervisor Comment — Suggested Reply", level=2)
    add_para(
        doc,
        "Thank you for the feedback. Section 3.4 has been updated to include the binary and "
        "multinomial (softmax) logistic regression equations. The system performs multiclass "
        "classification over 26 cattle diseases using multinomial logistic regression in "
        "Scikit-learn (solver='lbfgs', L2 regularization C=0.2). This model achieved 92.80% "
        "test accuracy and was deployed as the production classifier in the Django application.",
        italic=True,
    )

    doc.save(out_path)
    print(f"Created: {out_path}")


if __name__ == "__main__":
    main()
