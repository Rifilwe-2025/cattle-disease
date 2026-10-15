"""
MCP server for the Early Disease Prediction for Cattle system.

Exposes the trained disease-prediction model and the Django case database as
MCP tools, so an MCP client (Claude Code, Claude Desktop, ...) can run
predictions and inspect system data without going through the web UI.

Transport is stdio. Run with:
    venv\\Scripts\\python.exe -m mcp_server.server

All database tools are read-only.
"""
from __future__ import annotations

from mcp.server.mcpserver import MCPServer

from mcp_server.django_bootstrap import setup

setup()

from django.conf import settings  # noqa: E402  (must follow django.setup())
from django.db.models import Count  # noqa: E402

from cases.models import Case, Disease, Symptom  # noqa: E402
from farmers.models import Farmer  # noqa: E402
from ml_engine import services  # noqa: E402
from vets.models import Vet, VetApplication  # noqa: E402

app = MCPServer("cattle-disease-prediction")

# The 93 symptom columns the model was trained on, in training order.
# Mirrors SYMPTOM_COLS in ml_engine.services.predict_disease.
SYMPTOM_COLS = [
    'anorexia', 'abdominal_pain', 'anaemia', 'abortions', 'acetone',
    'aggression', 'arthrogyposis', 'ankylosis', 'anxiety', 'bellowing',
    'blood_loss', 'blood_poisoning', 'blisters', 'colic', 'Condemnation_of_livers',
    'conjunctivae', 'coughing', 'depression', 'discomfort', 'dyspnea',
    'dysentery', 'diarrhoea', 'dehydration', 'drooling', 'dull',
    'decreased_fertility', 'diffculty_breath', 'emaciation', 'encephalitis', 'fever',
    'facial_paralysis', 'frothing_of_mouth', 'frothing', 'gaseous_stomach', 'highly_diarrhoea',
    'high_pulse_rate', 'high_temp', 'high_proportion', 'hyperaemia', 'hydrocephalus',
    'isolation_from_herd', 'infertility', 'intermittent_fever', 'jaundice', 'ketosis',
    'loss_of_appetite', 'lameness', 'lack_of-coordination', 'lethargy', 'lacrimation',
    'milk_flakes', 'milk_watery', 'milk_clots', 'mild_diarrhoea', 'moaning',
    'mucosal_lesions', 'milk_fever', 'nausea', 'nasel_discharges', 'oedema',
    'pain', 'painful_tongue', 'pneumonia', 'photo_sensitization', 'quivering_lips',
    'reduction_milk_vields', 'rapid_breathing', 'rumenstasis', 'reduced_rumination', 'reduced_fertility',
    'reduced_fat', 'reduces_feed_intake', 'raised_breathing', 'stomach_pain', 'salivation',
    'stillbirths', 'shallow_breathing', 'swollen_pharyngeal', 'swelling', 'saliva',
    'swollen_tongue', 'tachycardia', 'torticollis', 'udder_swelling', 'udder_heat',
    'udder_hardeness', 'udder_redness', 'udder_pain', 'unwillingness_to_move', 'ulcers',
    'vomiting', 'weight_loss', 'weakness',
]


# ---------------------------------------------------------------------------
# Prediction tools
# ---------------------------------------------------------------------------

@app.tool()
def predict_disease(
    symptoms: list[str],
    age_years: int = 3,
    sex: str = "Female",
    breed: str = "Crossbreed",
    vaccinated: str = "No",
    herd_size: int = 20,
    farming_type: str = "Small-scale",
    recent_movement: str = "No",
    season: str = "Dry",
    province: str = "Harare",
) -> dict:
    """Predict cattle disease from observed symptoms and herd context.

    Runs the trained model (26 diseases) and returns the top prediction, its
    confidence, the top-3 ranked candidates, the severity classification and
    treatment recommendations.

    Args:
        symptoms: Symptom codes, e.g. ["fever", "coughing", "udder_swelling"].
            Call list_symptoms for valid codes. Unknown codes are returned in
            `unknown_symptoms` and ignored by the model.
        age_years: Age of the animal in years (1-8).
        sex: "Male" or "Female".
        breed: "Brahman", "Mashona", "Tuli" or "Crossbreed".
        vaccinated: "Yes" or "No".
        herd_size: Number of cattle in the herd (5-500).
        farming_type: "Communal", "Small-scale" or "Commercial".
        recent_movement: "Yes" or "No" - whether cattle moved recently.
        season: "Dry" or "Rainy".
        province: Zimbabwe province name.
    """
    known = [s for s in symptoms if s in SYMPTOM_COLS]
    unknown = [s for s in symptoms if s not in SYMPTOM_COLS]

    contextual = {
        'age_years': age_years,
        'sex': sex,
        'breed': breed,
        'vaccinated': vaccinated,
        'herd_size': herd_size,
        'farming_type': farming_type,
        'recent_movement': recent_movement,
        'season': season,
        'province': province,
    }

    result = services.predict_disease(known, contextual)

    if result.get('error'):
        return {
            'error': result['error'],
            'hint': 'Model artifacts may be missing. Check best_disease_model.pkl, '
                    'preprocessor.pkl and label_encoder.pkl in the project root.',
        }

    disease = result['disease']
    confidence = result['confidence']
    severity = services.classify_severity(confidence, disease)

    return {
        'predicted_disease': disease,
        'confidence': round(confidence, 4),
        'severity': severity,
        'top_3_diseases': result['top_3_diseases'],
        'recommendations': services.get_treatment_recommendations(disease, severity),
        'symptoms_used': known,
        'unknown_symptoms': unknown,
        'contextual_features': contextual,
    }


@app.tool()
def list_symptoms() -> dict:
    """List all 93 symptom codes the prediction model accepts.

    These codes are what predict_disease expects in its `symptoms` argument.
    """
    return {'count': len(SYMPTOM_COLS), 'symptoms': SYMPTOM_COLS}


@app.tool()
def list_diseases() -> dict:
    """List the 26 diseases the model can predict, with their severity ratings.

    Severity comes from settings.DISEASE_SEVERITY: the clinical danger of the
    disease drives the base severity, independent of model confidence.
    """
    severity_map = getattr(settings, 'DISEASE_SEVERITY', {})
    diseases = [
        {'code': code, 'severity': severity}
        for code, severity in sorted(severity_map.items(), key=lambda kv: (kv[1], kv[0]))
    ]
    return {'count': len(diseases), 'diseases': diseases}


@app.tool()
def model_info() -> dict:
    """Report the trained model's identity and evaluation metrics.

    Returns training date, test accuracy / F1 / precision / recall,
    cross-validation scores, feature counts and the dataset noise profile.
    """
    import json
    from pathlib import Path

    metadata_path = Path(settings.BASE_DIR) / 'model_metadata.json'
    if not metadata_path.exists():
        return {'error': 'model_metadata.json not found - run the training notebook first.'}

    with metadata_path.open(encoding='utf-8') as fh:
        metadata = json.load(fh)

    metadata['severity_thresholds'] = getattr(settings, 'SEVERITY_THRESHOLDS', {})
    return metadata


# ---------------------------------------------------------------------------
# Read-only database tools
# ---------------------------------------------------------------------------

def _case_summary(case: Case) -> dict:
    return {
        'id': case.id,
        'farmer': case.farmer.full_name,
        'province': case.farmer.province,
        'district': case.farmer.district,
        'assigned_vet': case.assigned_vet.full_name if case.assigned_vet else None,
        'symptoms': case.symptoms,
        'predicted_disease': case.predicted_disease,
        'confidence_score': round(case.confidence_score, 4) if case.confidence_score else None,
        'severity': case.severity,
        'status': case.status,
        'created_at': case.created_at.isoformat(),
    }


@app.tool()
def list_cases(
    status: str | None = None,
    severity: str | None = None,
    province: str | None = None,
    limit: int = 20,
) -> dict:
    """List submitted disease cases, newest first. Read-only.

    Args:
        status: Filter by status - PENDING, ASSIGNED, IN_PROGRESS, RESOLVED or CLOSED.
        severity: Filter by severity - NON_SEVERE, SEVERE or CRITICAL.
        province: Filter by the farmer's province.
        limit: Maximum cases to return (1-100).
    """
    queryset = Case.objects.select_related('farmer', 'assigned_vet')

    if status:
        queryset = queryset.filter(status=status.upper())
    if severity:
        queryset = queryset.filter(severity=severity.upper())
    if province:
        queryset = queryset.filter(farmer__province__iexact=province)

    total = queryset.count()
    limit = max(1, min(limit, 100))
    cases = [_case_summary(c) for c in queryset.order_by('-created_at')[:limit]]

    return {'total_matching': total, 'returned': len(cases), 'cases': cases}


@app.tool()
def get_case(case_id: int) -> dict:
    """Fetch one case in full, including the vet diagnosis and ranked predictions. Read-only.

    Args:
        case_id: Primary key of the case.
    """
    try:
        case = Case.objects.select_related('farmer', 'assigned_vet').get(pk=case_id)
    except Case.DoesNotExist:
        return {'error': f'No case with id {case_id}.'}

    detail = _case_summary(case)
    detail.update({
        'notes': case.notes,
        'top_diseases': case.top_diseases,
        'vet_diagnosis': case.vet_diagnosis,
        'vet_recommendations': case.vet_recommendations,
        'vet_consultation_date': (
            case.vet_consultation_date.isoformat() if case.vet_consultation_date else None
        ),
        'resolved_at': case.resolved_at.isoformat() if case.resolved_at else None,
        'updated_at': case.updated_at.isoformat(),
    })
    return detail


@app.tool()
def list_farmers(province: str | None = None, limit: int = 20) -> dict:
    """List registered farmers with their location and herd details. Read-only.

    Args:
        province: Filter by province.
        limit: Maximum farmers to return (1-100).
    """
    queryset = Farmer.objects.all()
    if province:
        queryset = queryset.filter(province__iexact=province)

    total = queryset.count()
    limit = max(1, min(limit, 100))

    farmers = [
        {
            'id': f.id,
            'full_name': f.full_name,
            'province': f.province,
            'district': f.district,
            'cattle_breed': f.cattle_breed,
            'number_of_cattle': f.number_of_cattle,
            'farming_type': f.farming_type,
            'has_gps': f.has_location(),
            'case_count': f.cases.count(),
        }
        for f in queryset.order_by('-created_at')[:limit]
    ]
    return {'total_matching': total, 'returned': len(farmers), 'farmers': farmers}


@app.tool()
def list_vets(province: str | None = None, available_only: bool = False, limit: int = 20) -> dict:
    """List approved veterinarians and the provinces they serve. Read-only.

    Args:
        province: Only vets serving this province.
        available_only: Restrict to vets currently accepting new cases.
        limit: Maximum vets to return (1-100).
    """
    queryset = Vet.objects.filter(is_approved=True)
    if available_only:
        queryset = queryset.filter(is_available=True)

    total = queryset.count()
    limit = max(1, min(limit, 100))

    vets = []
    for v in queryset.order_by('-created_at'):
        served = v.provinces_served or []
        if province and province not in served:
            continue
        vets.append({
            'id': v.id,
            'full_name': v.full_name,
            'license_number': v.license_number,
            'qualification': v.qualification,
            'years_of_experience': v.years_of_experience,
            'provinces_served': served,
            'is_available': v.is_available,
            'assigned_case_count': v.assigned_cases.count(),
        })
        if len(vets) >= limit:
            break

    return {'total_approved': total, 'returned': len(vets), 'vets': vets}


@app.tool()
def system_stats() -> dict:
    """Summarise the system: case counts by status and severity, top diseases, user totals.

    Read-only. A good first call to understand the current state of the database.
    """
    by_status = dict(
        Case.objects.values_list('status').annotate(n=Count('id')).values_list('status', 'n')
    )
    by_severity = dict(
        Case.objects.values_list('severity').annotate(n=Count('id')).values_list('severity', 'n')
    )
    top_diseases = [
        {'disease': row['predicted_disease'], 'cases': row['n']}
        for row in Case.objects.values('predicted_disease')
                               .annotate(n=Count('id'))
                               .order_by('-n')[:10]
    ]

    return {
        'cases': {
            'total': Case.objects.count(),
            'by_status': by_status,
            'by_severity': by_severity,
            'top_predicted_diseases': top_diseases,
        },
        'farmers': Farmer.objects.count(),
        'vets': {
            'approved': Vet.objects.filter(is_approved=True).count(),
            'available': Vet.objects.filter(is_approved=True, is_available=True).count(),
            'pending_applications': VetApplication.objects.filter(status='PENDING').count(),
        },
        'reference_data': {
            'diseases_in_db': Disease.objects.count(),
            'symptoms_in_db': Symptom.objects.count(),
        },
    }


@app.tool()
def disease_stats_by_province(province: str | None = None) -> dict:
    """Break down cases by province and predicted disease - an outbreak view. Read-only.

    Args:
        province: Restrict to one province. Omit for a nationwide breakdown.
    """
    queryset = Case.objects.select_related('farmer')
    if province:
        queryset = queryset.filter(farmer__province__iexact=province)

    rows = (
        queryset.values('farmer__province', 'predicted_disease', 'severity')
                .annotate(n=Count('id'))
                .order_by('farmer__province', '-n')
    )

    breakdown: dict[str, dict] = {}
    for row in rows:
        prov = row['farmer__province'] or 'Unknown'
        entry = breakdown.setdefault(prov, {'total_cases': 0, 'diseases': []})
        entry['total_cases'] += row['n']
        entry['diseases'].append({
            'disease': row['predicted_disease'],
            'severity': row['severity'],
            'cases': row['n'],
        })

    return {'provinces_covered': len(breakdown), 'breakdown': breakdown}


if __name__ == '__main__':
    app.run()
