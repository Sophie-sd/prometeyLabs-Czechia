"""Language switcher for i18n_patterns(..., prefix_default_language=False).

Stock ``django.views.i18n.set_language`` uses ``translate_url``, which
``resolve``-s ``next`` under the *current* language prefix. That fails for
unprefixed default-language URLs: POST CS from ``/en/`` would redirect
back to ``/en/``.

PrometeyLabs Czechia: default ``cs`` (no prefix), ``en`` with ``/en/``.
"""
from __future__ import annotations

import re
from urllib.parse import unquote, urlsplit, urlunsplit

from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import NoReverseMatch, Resolver404, resolve, reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import check_for_language, override
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST
from django.views.i18n import LANGUAGE_QUERY_PARAMETER


def _prefixed_language_codes() -> tuple[str, ...]:
    default = (settings.LANGUAGE_CODE or 'cs').split('-')[0]
    codes = []
    for code, _name in settings.LANGUAGES:
        short = code.split('-')[0]
        if short and short != default and short not in codes:
            codes.append(short)
    return tuple(codes)


def _prefix_re() -> re.Pattern[str]:
    codes = _prefixed_language_codes()
    if not codes:
        return re.compile(r'^\b\B')  # never matches
    return re.compile(r'^/(' + '|'.join(re.escape(c) for c in codes) + r')(?=/|$)')


def strip_lang_prefix(path: str) -> str:
    stripped = _prefix_re().sub('', path or '')
    if not stripped.startswith('/'):
        stripped = '/' + stripped
    return stripped or '/'


def translate_path(url: str, lang_code: str) -> str:
    """Rewrite ``url`` to ``lang_code``, including default language with no prefix."""
    parsed = urlsplit(url)
    unprefixed = strip_lang_prefix(unquote(parsed.path or '/'))
    new_path = unprefixed
    try:
        with override(settings.LANGUAGE_CODE):
            match = resolve(unprefixed)
        viewname = (
            f'{match.namespace}:{match.url_name}'
            if match.namespace
            else match.url_name
        )
        if viewname:
            with override(lang_code):
                new_path = reverse(viewname, args=match.args, kwargs=match.kwargs)
    except (Resolver404, NoReverseMatch, TypeError):
        default = (settings.LANGUAGE_CODE or 'cs').split('-')[0]
        target = (lang_code or default).split('-')[0]
        if target == default:
            new_path = unprefixed
        elif unprefixed == '/':
            new_path = f'/{target}/'
        else:
            new_path = f'/{target}{unprefixed}'
    return urlunsplit(
        (parsed.scheme, parsed.netloc, new_path, parsed.query, parsed.fragment),
    )


def _redirect_target(request, next_url: str | None) -> str | None:
    allowed = {request.get_host()}
    require_https = request.is_secure()
    if (
        next_url or request.accepts('text/html')
    ) and not url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts=allowed,
        require_https=require_https,
    ):
        next_url = request.META.get('HTTP_REFERER')
        if not url_has_allowed_host_and_scheme(
            url=next_url,
            allowed_hosts=allowed,
            require_https=require_https,
        ):
            next_url = '/'
    return next_url


@never_cache
@require_POST
def set_language(request):
    next_url = _redirect_target(
        request,
        request.POST.get('next', request.GET.get('next')),
    )
    response = HttpResponseRedirect(next_url) if next_url else HttpResponse(status=204)
    lang_code = request.POST.get(LANGUAGE_QUERY_PARAMETER)
    if lang_code and check_for_language(lang_code):
        if next_url:
            next_trans = translate_path(next_url, lang_code)
            if next_trans != next_url:
                response = HttpResponseRedirect(next_trans)
        response.set_cookie(
            settings.LANGUAGE_COOKIE_NAME,
            lang_code,
            max_age=settings.LANGUAGE_COOKIE_AGE,
            path=settings.LANGUAGE_COOKIE_PATH,
            domain=settings.LANGUAGE_COOKIE_DOMAIN,
            secure=settings.LANGUAGE_COOKIE_SECURE,
            httponly=settings.LANGUAGE_COOKIE_HTTPONLY,
            samesite=settings.LANGUAGE_COOKIE_SAMESITE,
        )
    return response
