"""Template tag resolving admin URLs on whichever admin site is being browsed."""
from django import template

from apps.demoshop.admin_nav import resolve_admin_url

register = template.Library()


@register.simple_tag(takes_context=True)
def admin_url(context, view_name):
    """`{% admin_url 'demoshop_shopproduct_changelist' %}` → /admin/… or /demo-admin/…"""
    request = context.get('request')
    if request is None:
        from django.urls import reverse

        return reverse(f'admin:{view_name}')
    return resolve_admin_url(request, view_name)
