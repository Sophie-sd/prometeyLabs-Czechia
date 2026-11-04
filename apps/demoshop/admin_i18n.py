"""Third-party admin strings the demo client must never see in English.

Unfold ships no `locale/` catalogue at all, so its English literals reach the
Czech demo admin untranslated. `LOCALE_PATHS` wins over app catalogues, so the
project catalogue can translate them — but `makemessages` only keeps msgids it
can find in our own sources, hence these declarations.

Nothing imports the names; the module exists so `makemessages` sees the strings.
"""
from django.utils.translation import gettext_noop as _

# django-unfold: header, sidebar search and theme switcher.
_('Search apps and models...')
_('Type to search')
_('Light')
_('Dark')
_('System')
_('Toggle sidebar')
_('Toggle dark/light mode')
_('All applications')

# django-unfold: widgets and empty states.
_('Select value')
_('No results found')
_('This page yielded into no results. Create a new item or reset your filters.')
_('Reset filters')
_('Clear all filters')
_('Apply Filters')
_('Show counts')
_('Hide counts')
_('Clear')
_('Currently')
_('Change')

# apps/demoshop/demo_admin_site.py — DemoAdminSite headers.
_('Demo Shop Administration')
_('Demo Admin')
_('Manage Your Demo Shop')
