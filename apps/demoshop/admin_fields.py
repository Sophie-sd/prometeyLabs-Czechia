"""Keeping legacy base columns in sync while the demo admin only edits cs/en.

The catalog models predate the Czech site and keep a language-less base column
(`name`, `description`, …) next to `_ru` / `_en` / `_cs` variants. The base column
still drives `slug` and the `localized_text(base, ru, en, cs)` fallback, so when
the client's form stops showing it we mirror the Czech value into it on save.
"""


def mirror_cs_into_base(obj, mapping: dict) -> None:
    """Copy `<field>_cs` (or `<field>_en` as a last resort) into `<field>`."""
    for base_field, cs_field in mapping.items():
        value = (getattr(obj, cs_field, '') or '').strip()
        if not value:
            en_field = f'{base_field}_en'
            value = (getattr(obj, en_field, '') or '').strip()
        if value:
            setattr(obj, base_field, value)
