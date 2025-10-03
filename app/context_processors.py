import os
from pathlib import Path

from django.conf import settings


def static_version(request):
    """Return a simple cache-busting version for static files based on file mtime.

    Looks for the collected static file in STATIC_ROOT first, then falls back to the
    app static path. Returns an integer timestamp or empty string on errors.
    """
    try:
        base_dir = Path(settings.BASE_DIR)
        candidates = []
        # prefer collected static (STATIC_ROOT)
        if getattr(settings, 'STATIC_ROOT', None):
            candidates.append(Path(settings.STATIC_ROOT) / 'css' / 'style.css')
        # fall back to app static path
        candidates.append(base_dir / 'app' / 'static' / 'css' / 'style.css')

        for p in candidates:
            if p.exists():
                return {'static_version': str(int(p.stat().st_mtime))}
    except Exception:
        pass
    return {'static_version': ''}
