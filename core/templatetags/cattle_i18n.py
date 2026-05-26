from django import template

from core import cattle_terms

register = template.Library()


@register.filter
def local_symptom(value):
    return cattle_terms.get_symptom_label(value)


@register.filter
def local_disease(value):
    return cattle_terms.get_disease_label(value)


@register.filter
def local_case_status(value):
    return cattle_terms.get_case_status_label(value)


@register.filter
def local_severity(value):
    return cattle_terms.get_severity_label(value)
