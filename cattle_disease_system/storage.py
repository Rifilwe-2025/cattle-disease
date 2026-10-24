"""
Static files storage for the project.

Split out of settings.py because STORAGES takes an import path, not a class.
"""
from whitenoise.storage import CompressedManifestStaticFilesStorage


class ForgivingManifestStaticFiles(CompressedManifestStaticFilesStorage):
    """
    Hashed, compressed static files that do not 500 on a missing reference.

    Manifest storage normally raises ValueError when a template asks for a file
    that was not collected, which turns a single stale ``{% static %}`` path
    into a broken page in production while working fine under DEBUG (where
    manifest storage is bypassed entirely). With ``manifest_strict = False``
    the unknown path is passed through unhashed: the image 404s, the page
    renders.

    ``CompressedManifestStaticFilesStorage`` also writes .gz and .br siblings
    at collectstatic time, so WhiteNoise serves pre-compressed bytes rather
    than compressing on every request.
    """

    manifest_strict = False
