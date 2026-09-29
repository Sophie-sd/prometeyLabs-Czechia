"""Localized DB-backed content helpers for PrometeyLabs Czechia (cs + en)."""
from __future__ import annotations

from django.utils import translation


def localized_text(
    default_value: str | None,
    ru_value: str | None = None,
    en_value: str | None = None,
    cs_value: str | None = None,
) -> str:
    """Pick text for the active language.

    Call sites historically pass ``(base, ru, en, cs)`` where ``base`` held
    Ukrainian. For Czechia, ``base`` / ``default_value`` is Czech (or the
    legacy primary field). English uses ``en_value``. Russian is never the
    primary fallback.
    """
    default = (default_value or '').strip()
    en = (en_value or '').strip()
    cs = (cs_value or '').strip()
    # ru_value intentionally unused as a primary path
    _ = ru_value
    lang = (translation.get_language() or 'cs').split('-')[0]
    if lang == 'en' and en:
        return en
    if lang == 'cs':
        return cs or default
    return cs or default or en


def is_ru_language() -> bool:
    """Deprecated on Czechia; always False for primary routing."""
    return False


def translate_ua_to_ru(text: str) -> str:
    """No-op stub kept for import compatibility; UA→RU is not used on Czechia."""
    return text or ''
