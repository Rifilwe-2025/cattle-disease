"""
Email notifications for case events.

Kept out of the views so the message content is testable on its own, and so the
rule in core.mailer holds: the message is fully rendered here, while a request
is still in scope, and only finished strings cross onto the sending thread.
Reading ``case.farmer.full_name`` from inside that thread would mean a database
query on a connection the request is also using.
"""
import logging

from django.conf import settings
from django.urls import reverse
from django.utils.html import escape

from core.mailer import send_email

logger = logging.getLogger(__name__)

SEVERITY_LABEL = {
    'CRITICAL': 'CRITICAL - emergency',
    'SEVERE': 'Severe',
    'NON_SEVERE': 'Non-severe',
}


def _absolute(path, request=None):
    """
    Turn a path into a link that still works from inside an inbox.

    ``request.build_absolute_uri`` is preferred because it picks up the host
    actually being served, which matters once a custom domain sits alongside
    the onrender.com one. SITE_URL is the fallback for mail sent with no
    request in scope.
    """
    if request is not None:
        return request.build_absolute_uri(path)
    return f"{settings.SITE_URL.rstrip('/')}{path}"


def _humanise(value):
    """'foot_and_mouth' -> 'Foot And Mouth'."""
    return str(value or '').replace('_', ' ').title()


def _doctor(full_name):
    """
    'Dr. X' from a vet's name, whichever way the name was entered.

    Vet.full_name is free text and some rows already carry the title
    ('Dr. Tawanda Ncube'), so prefixing unconditionally produced
    'Dear Dr. Dr. Tawanda Ncube'.
    """
    bare = str(full_name or '').strip()
    lowered = bare.lower()
    for prefix in ('doctor ', 'dr. ', 'dr '):
        if lowered.startswith(prefix):
            bare = bare[len(prefix):].strip()
            break
    else:
        if lowered in ('dr', 'dr.', 'doctor'):
            bare = ''
    return f'Dr. {bare}' if bare else 'Doctor'


def notify_vet_of_assignment(case, request=None):
    """
    Tell a vet that a farmer has chosen them for a case.

    Sent the moment the farmer submits their vet selection. The vet's profile
    email is the target, falling back to the address on their user account - a
    vet who registered before the profile email was collected still has one
    there.

    Reply-To is set to the farmer, so a vet replying in their mail client
    reaches the farmer directly rather than the system's send address.

    Returns True if a message was queued, False if the vet has no address on
    file. Never raises: assignment must not fail because mail failed.
    """
    vet = case.assigned_vet
    if vet is None:
        logger.warning("Case %s has no assigned vet to notify", case.pk)
        return False

    farmer = case.farmer
    recipient = (vet.email or '').strip() or (getattr(vet.user, 'email', '') or '').strip()
    if not recipient:
        logger.warning(
            "Vet %s (case %s) has no email address on file; no notification sent",
            vet.pk, case.pk,
        )
        return False

    case_url = _absolute(reverse('vets:case_detail', kwargs={'case_id': case.pk}), request)
    disease = _humanise(case.predicted_disease)
    severity = SEVERITY_LABEL.get(case.severity, case.severity)
    symptoms = [_humanise(s) for s in (case.symptoms or [])]
    confidence = f'{case.confidence_score * 100:.0f}%'

    urgent = case.severity == 'CRITICAL'
    prefix = '[URGENT] ' if urgent else ''
    subject = (
        f'{prefix}New case assigned to you - {disease} ({severity}) - Case #{case.pk}'
    )

    lines = [
        f'Dear {_doctor(vet.full_name)},',
        '',
        f'{farmer.full_name} has selected you to review a case reported through '
        f'CattleCare AI.',
        '',
        f'Case number:        #{case.pk}',
        f'Severity:           {severity}',
        f'AI prediction:      {disease} ({confidence} confidence)',
        f'Reported symptoms:  {", ".join(symptoms) if symptoms else "None recorded"}',
        '',
        'Farmer',
        f'  Name:     {farmer.full_name}',
        f'  Phone:    {farmer.phone_number or "not provided"}',
        f'  Email:    {farmer.email or "not provided"}',
        f'  Location: {farmer.district}, {farmer.province}',
        f'  Herd:     {farmer.number_of_cattle or "unknown"} head, '
        f'{farmer.cattle_breed or "breed not recorded"}',
    ]

    if case.notes:
        lines += ['', 'Notes from the farmer', f'  {case.notes}']

    # The model's alternatives appear only when it was unsure, which is the
    # rule the vet's own dashboard already follows: a confident single
    # prediction shown with a list of runners-up underneath reads as less
    # certain than it actually is.
    if case.top_diseases:
        lines += ['', 'The model was not confident. Its top alternatives were:']
        for entry in case.top_diseases:
            name = _humanise(entry.get('disease'))
            pct = float(entry.get('probability', 0)) * 100
            lines.append(f'  - {name}: {pct:.0f}%')

    lines += [
        '',
        'Open the case to record your diagnosis and recommendation:',
        case_url,
        '',
    ]

    if urgent:
        lines += [
            'This case is classed CRITICAL. The farmer has been told to isolate '
            'the affected animal and await emergency veterinary attention.',
            '',
        ]

    lines += [
        'You can reply directly to this email to reach the farmer.',
        '',
        '- CattleCare AI',
    ]

    html_body = _assignment_html(
        vet=vet, farmer=farmer, case=case, case_url=case_url,
        disease=disease, severity=severity, confidence=confidence,
        symptoms=symptoms, urgent=urgent,
    )

    return send_email(
        subject=subject,
        body='\n'.join(lines),
        recipients=[recipient],
        html_body=html_body,
        reply_to=[farmer.email] if farmer.email else None,
    )


def _assignment_html(*, vet, farmer, case, case_url, disease, severity,
                     confidence, symptoms, urgent):
    """
    The HTML alternative for the assignment notification.

    Written as nested tables with inline styles on purpose. Mail clients are
    not browsers: Outlook ignores most of a stylesheet, Gmail strips <style>
    from a forwarded copy, and neither can be relied on for flexbox or CSS
    custom properties. Inline attributes on tables is the shape that survives
    all of them, however dated it looks beside the rest of the project's CSS.

    Every interpolated value is escaped. The farmer's free-text notes reach
    this template verbatim and are the one field a user fully controls.
    """
    accent = '#b91c1c' if urgent else '#2d5a4a'
    eyebrow = 'Urgent - new case' if urgent else 'New case assigned'

    def rows(pairs, nowrap):
        wrap = ';white-space:nowrap' if nowrap else ''
        return ''.join(
            '<tr>'
            f'<td style="padding:5px 16px 5px 0;color:#6b7280;font-size:14px;'
            f'vertical-align:top{wrap}">{escape(label)}</td>'
            f'<td style="padding:5px 0;color:#111827;font-size:14px">'
            f'{escape(value)}</td>'
            '</tr>'
            for label, value in pairs
        )

    detail_rows = rows((
        ('Case number', f'#{case.pk}'),
        ('Severity', severity),
        ('AI prediction', f'{disease} ({confidence} confidence)'),
        ('Symptoms', ', '.join(symptoms) if symptoms else 'None recorded'),
    ), nowrap=True)

    farmer_rows = rows((
        ('Name', farmer.full_name),
        ('Phone', farmer.phone_number or 'not provided'),
        ('Email', farmer.email or 'not provided'),
        ('Location', f'{farmer.district}, {farmer.province}'),
    ), nowrap=True)

    notes_block = ''
    if case.notes:
        notes_block = (
            '<p style="margin:0 0 4px;color:#6b7280;font-size:13px;'
            'text-transform:uppercase;letter-spacing:.04em">'
            'Notes from the farmer</p>'
            '<p style="margin:0 0 24px;padding:12px 14px;background:#f9fafb;'
            'border-left:3px solid #d1d5db;color:#374151;font-size:14px;'
            f'line-height:1.6">{escape(case.notes)}</p>'
        )

    urgent_block = ''
    if urgent:
        urgent_block = (
            '<p style="margin:0 0 24px;padding:12px 14px;background:#fef2f2;'
            'border-left:3px solid #b91c1c;color:#991b1b;font-size:14px;'
            'line-height:1.6"><strong>This case is classed CRITICAL.</strong> '
            'The farmer has been told to isolate the affected animal and await '
            'emergency veterinary attention.</p>'
        )

    return f"""<!DOCTYPE html>
<html><body style="margin:0;padding:24px 12px;background:#f3f4f6;
  font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif">
<table role="presentation" cellpadding="0" cellspacing="0" border="0"
       style="max-width:600px;margin:0 auto;background:#ffffff;border-radius:12px;
              overflow:hidden">
  <tr><td style="height:4px;background:{accent}"></td></tr>
  <tr><td style="padding:32px 32px 8px">
    <p style="margin:0 0 4px;color:{accent};font-size:12px;font-weight:700;
              text-transform:uppercase;letter-spacing:.08em">{eyebrow}</p>
    <h1 style="margin:0 0 20px;color:#111827;font-size:22px;font-weight:700">
      {escape(disease)}</h1>
    <p style="margin:0 0 24px;color:#374151;font-size:15px;line-height:1.6">
      Dear {escape(_doctor(vet.full_name))}, {escape(farmer.full_name)} has selected
      you to review a case reported through CattleCare AI.</p>

    <table role="presentation" cellpadding="0" cellspacing="0" border="0"
           style="width:100%;margin:0 0 24px;background:#f9fafb;
                  border-radius:8px">{detail_rows}</table>

    <p style="margin:0 0 4px;color:#6b7280;font-size:13px;
              text-transform:uppercase;letter-spacing:.04em">Farmer</p>
    <table role="presentation" cellpadding="0" cellspacing="0" border="0"
           style="width:100%;margin:0 0 24px">{farmer_rows}</table>

    {notes_block}
    {urgent_block}

    <table role="presentation" cellpadding="0" cellspacing="0" border="0"
           style="margin:0 0 24px">
      <tr><td style="background:{accent};border-radius:8px">
        <a href="{escape(case_url)}"
           style="display:inline-block;padding:13px 26px;color:#ffffff;
                  font-size:15px;font-weight:600;text-decoration:none">
          Open case #{case.pk}</a>
      </td></tr>
    </table>

    <p style="margin:0 0 32px;color:#6b7280;font-size:13px;line-height:1.6">
      You can reply directly to this email to reach the farmer.</p>
  </td></tr>
  <tr><td style="padding:16px 32px;background:#f9fafb;border-top:1px solid #e5e7eb">
    <p style="margin:0;color:#9ca3af;font-size:12px">
      CattleCare AI &middot; Early Disease Prediction for Cattle</p>
  </td></tr>
</table>
</body></html>"""
