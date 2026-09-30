"""
CSP (Content Security Policy) middleware.

Generates a per-request nonce and adds a Content-Security-Policy response header.
The nonce is exposed to templates via the `csp_nonce` context variable (see
context_processors.py).  Every inline <script nonce="{{ csp_nonce }}"> tag must
use this nonce — otherwise the browser will block it.

Allowed external origins are kept conservative; extend the lists below if new
third-party services are added.
"""
import secrets


class CSPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        nonce = secrets.token_hex(16)
        request.csp_nonce = nonce

        response = self.get_response(request)

        # Skip non-HTML responses (JSON API, redirects, static files, etc.)
        content_type = response.get('Content-Type', '')
        if 'text/html' not in content_type:
            return response

        # Django admin ships its own JS/CSS bundle and uses inline event
        # handlers in some widgets. Applying 'strict-dynamic' here breaks the
        # nav sidebar, inline "Add another" buttons, autocomplete, etc., so we
        # leave the admin out of the CSP entirely. Admin is an internal,
        # authenticated tool and is not exposed to anonymous traffic.
        path = request.path_info or ''
        if path.startswith('/admin/') or path == '/admin':
            return response

        # Google Fonts load via protocol-relative URLs (//…).
        # On http://localhost that becomes http://, so both schemes must be allowed.
        script_src = (
            f"'self' 'nonce-{nonce}' 'strict-dynamic' 'unsafe-eval' "
            "https://www.googletagmanager.com "
            "https://cdn-cookieyes.com "
            "https://connect.facebook.net "
            "https://scripts.clixtell.com "
            "https://tracker.clixtell.com "
            "https://www.google.com "
            "https://www.google-analytics.com "
            "https://googleads.g.doubleclick.net "
            "https://www.googleadservices.com"
        )
        csp = "; ".join([
            "default-src 'self'",
            f"script-src {script_src}",
            (
                "style-src 'self' 'unsafe-inline' "
                "https://fonts.googleapis.com http://fonts.googleapis.com"
            ),
            "img-src 'self' data: https: blob:",
            (
                "font-src 'self' data: "
                "https://fonts.gstatic.com http://fonts.gstatic.com"
            ),
            "frame-src 'self' https://www.google.com https://maps.google.com "
            "https://www.googletagmanager.com https://bid.g.doubleclick.net "
            "https://www.facebook.com https://td.doubleclick.net",
            (
                "connect-src 'self' https: "
                "https://cdn-cookieyes.com "
                "https://log.cookieyes.com "
                "https://directory.cookieyes.com"
            ),
            "media-src 'self' data: blob:",
            "worker-src 'self' blob:",
        ])
        response['Content-Security-Policy'] = csp
        return response


class AdminLocaleMiddleware:
    """Force Ukrainian for Django/Unfold admin without touching public CS/EN i18n.

    Public LANGUAGES stay cs+en. Admin path activates Django's built-in `uk`
    catalog (and any project locale/uk if added later).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        from django.utils import translation

        path = request.path_info or ""
        if path == "/admin" or path.startswith("/admin/"):
            translation.activate("uk")
            request.LANGUAGE_CODE = "uk"
        return self.get_response(request)

