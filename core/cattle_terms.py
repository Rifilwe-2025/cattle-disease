"""
Localized *display* labels for cattle symptoms and diseases.
Internal keys stay in English for the ML pipeline; templates use this for Shona/Ndebele.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from django.utils import translation

_DATA_PATH = Path(__file__).resolve().parent / 'cattle_terms_data.json'

CASE_STATUS_I18N: dict[str, dict[str, str]] = {
    'PENDING': {
        'en': 'Pending',
        'sn': 'Kumirira',
        'nd': 'Ilindile',
    },
    'ASSIGNED': {
        'en': 'Assigned to Vet',
        'sn': 'Yakapiwa kuveti',
        'nd': 'Yabelwe udokotela',
    },
    'IN_PROGRESS': {
        'en': 'In Progress',
        'sn': 'Irikushanda',
        'nd': 'Iyasebenza',
    },
    'RESOLVED': {
        'en': 'Resolved',
        'sn': 'Yagadziriswa',
        'nd': 'Ixazululiwe',
    },
    'CLOSED': {
        'en': 'Closed',
        'sn': 'Yavharwa',
        'nd': 'Ivaliwe',
    },
}

SEVERITY_I18N: dict[str, dict[str, str]] = {
    'NON_SEVERE': {
        'en': 'Non-Severe',
        'sn': 'Haisi yakanyanya',
        'nd': 'Ayisilo esikhulu',
    },
    'SEVERE': {
        'en': 'Severe',
        'sn': 'Yakakosha',
        'nd': 'Ebucayi',
    },
    'CRITICAL': {
        'en': 'Critical',
        'sn': 'Yakatyisa',
        'nd': 'Kubheka ngokushesha',
    },
}


@lru_cache(maxsize=1)
def _load_data() -> dict:
    if not _DATA_PATH.exists():
        return {'symptoms': {}, 'diseases': {}}
    return json.loads(_DATA_PATH.read_text(encoding='utf-8'))


def _active_lang() -> str:
    lang = (translation.get_language() or 'en').lower()
    return lang.split('-')[0]


def _pick(row: dict, lang: str) -> str:
    if not row:
        return ''
    return row.get(lang) or row.get('en') or ''


def normalize_disease_key(name: str | None) -> str:
    if not name:
        return ''
    return name.strip().lower().replace(' ', '_').replace('-', '_')


def get_symptom_label(key: str | None) -> str:
    """Display label for a symptom storage key (e.g. fever)."""
    if not key:
        return ''
    data = _load_data()
    row = data.get('symptoms', {}).get(key.strip())
    if row:
        return _pick(row, _active_lang())
    return key.replace('_', ' ').replace('-', ' ').title()


def get_disease_label(name: str | None) -> str:
    """Display label for predicted disease (label_encoder class)."""
    if not name:
        return ''
    raw = name.strip()
    lang = _active_lang()
    if raw.lower() in ('unknown', ''):
        if lang == 'sn':
            return 'Hazvizivikanwe'
        if lang == 'nd':
            return 'Akwaziwa'
        return 'Unknown'

    data = _load_data()
    norm = normalize_disease_key(raw)
    row = data.get('diseases', {}).get(norm)
    if row:
        return _pick(row, lang)
    # Allow pretty English if key not in table
    return raw.replace('_', ' ').replace('-', ' ').title()


def get_case_status_label(code: str | None) -> str:
    if not code:
        return ''
    row = CASE_STATUS_I18N.get(code.upper(), {})
    return _pick(row, _active_lang()) or code.replace('_', ' ').title()


def get_severity_label(code: str | None) -> str:
    if not code:
        return ''
    row = SEVERITY_I18N.get(code.upper(), {})
    return _pick(row, _active_lang()) or code.replace('_', ' ').title()
