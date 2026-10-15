"""
Boots Django outside of manage.py so the MCP server can use the ORM and ml_engine.

Imported for its side effect; call setup() once before touching any Django code.
"""
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

_ready = False


def setup():
    """Configure Django. Idempotent."""
    global _ready
    if _ready:
        return

    if str(BASE_DIR) not in sys.path:
        sys.path.insert(0, str(BASE_DIR))

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cattle_disease_system.settings')

    import django
    django.setup()
    _ready = True
