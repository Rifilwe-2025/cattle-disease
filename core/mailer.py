"""
Outbound email for the project.

Everything that sends mail goes through :func:`send_email` rather than calling
``django.core.mail.send_mail`` directly, for two reasons.

**It does not block the request.** An SMTP send is a TCP connect, a TLS
handshake and several round trips to Gmail. From a free Render instance in
Oregon that is routinely 2-5 seconds, and occasionally the full socket
timeout. Done inline, the farmer who picks a vet sits on a spinner for the
duration, and a vet's notification email is allowed to make case assignment
*look* broken. So the send happens on a short-lived background thread and the
view returns immediately.

**It cannot take a page down.** A failed send is logged and swallowed. Mail is
a notification, never the record: the case is already saved, the password reset
token is already valid. The one exception is where the user is told to go and
check their inbox, which is why :func:`send_email` still reports whether the
message was handed off.

Why a thread and not a task queue
---------------------------------
Celery or RQ would need a broker and a second Render service; this app is on
the free plan with no Redis. A thread is the honest fit for the volume
involved (a handful of messages a day), and its one real weakness is
acknowledged rather than hidden: a message queued microseconds before the
worker is recycled can be lost, because the thread is a daemon and will not
hold up shutdown. For password resets that is survivable - the user can ask
again - and it is strictly better than the alternative of holding a gunicorn
worker hostage to Gmail's latency.

The rule that makes the threading safe: **the caller renders the message, the
thread only transmits it.** Nothing passed across the boundary may be a model
instance or a lazy object, because the thread has no request, no active
language, and must not touch the database connection the request is using.
"""
import logging
import threading

from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection

logger = logging.getLogger(__name__)


def _deliver(subject, body, html_body, recipients, reply_to):
    """Open a connection, send one message, close it. Runs on the worker thread."""
    try:
        connection = get_connection(fail_silently=False)
        message = EmailMultiAlternatives(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipients,
            reply_to=reply_to or None,
            connection=connection,
        )
        if html_body:
            message.attach_alternative(html_body, 'text/html')
        message.send()
        logger.info("Email sent: %r -> %s", subject, ', '.join(recipients))
    except Exception as exc:  # noqa: BLE001 - a thread must not raise
        # Logged with a traceback rather than re-raised: there is no request to
        # return an error to, and an unhandled exception here would only print
        # a bare thread death.
        logger.exception(
            "Email FAILED: %r -> %s: %s", subject, ', '.join(recipients), exc
        )


def send_email(subject, body, recipients, html_body=None, reply_to=None,
               background=True):
    """
    Send one message to one or more recipients.

    Args:
        subject: Plain subject line.
        body: Plain-text body. Always provide one - some mail clients, and
            every screen reader, prefer it, and it is what lands in a spam
            filter's reading of the message.
        recipients: List of email addresses. Falsy entries are dropped, which
            is deliberate: a Vet row with a blank email should mean "no
            notification", not a crash inside case assignment.
        html_body: Optional HTML alternative.
        reply_to: Optional list of Reply-To addresses. Used so a vet can reply
            straight to the farmer who reported the case.
        background: Send on a worker thread (the default). Pass False from
            management commands and tests, where the process may exit before a
            daemon thread finishes and where a synchronous failure is what you
            actually want to see.

    Returns:
        True if the message was sent (or handed to a thread), False if there
        was no usable recipient.
    """
    recipients = [r.strip() for r in (recipients or []) if r and r.strip()]
    if not recipients:
        logger.warning("Email %r not sent: no valid recipient address", subject)
        return False

    if not background:
        _deliver(subject, body, html_body, recipients, reply_to)
        return True

    thread = threading.Thread(
        target=_deliver,
        args=(subject, body, html_body, recipients, reply_to),
        name=f'email-{subject[:30]}',
        daemon=True,
    )
    thread.start()
    return True


def is_smtp_configured():
    """
    True when real mail will leave the building.

    The console backend is the fallback when EMAIL_HOST_USER/PASSWORD are
    unset, and it prints to the log instead of sending. Views use this to tell
    the user "check your inbox" only when there is actually going to be
    something in it.
    """
    return 'smtp' in settings.EMAIL_BACKEND.lower()
