"""Admin-site-aware URL resolution for the sidebar shared by /admin/ and /demo-admin/.

The Unfold sidebar is declared once in settings but rendered on both admin sites.
A demo client lives on /demo-admin/ and has `is_staff=False`, so every hardcoded
`admin:` route in that menu is a dead end for them (302 to the staff login).
"""
from django.urls import NoReverseMatch, reverse

DEMO_ADMIN_PREFIX = '/demo-admin/'
DEMO_ADMIN_NAMESPACE = 'demo_admin'
STAFF_ADMIN_NAMESPACE = 'admin'


def admin_namespace_for(request) -> str:
    path = getattr(request, 'path_info', '') or ''
    if path.startswith(DEMO_ADMIN_PREFIX) or path == DEMO_ADMIN_PREFIX.rstrip('/'):
        return DEMO_ADMIN_NAMESPACE
    return STAFF_ADMIN_NAMESPACE


def resolve_admin_url(request, view_name: str) -> str:
    """Reverse `view_name` on the admin site the request is actually browsing."""
    namespace = admin_namespace_for(request)
    try:
        return reverse(f'{namespace}:{view_name}')
    except NoReverseMatch:
        return reverse(f'{STAFF_ADMIN_NAMESPACE}:{view_name}')


def admin_site_url(view_name: str):
    """Build an Unfold sidebar `link` callable for `view_name`."""

    def link(request):
        return resolve_admin_url(request, view_name)

    return link
