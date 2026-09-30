"""Generic registry-driven dynamic form для CMS-блоків тенанта.

Реєстр (`BLOCK_REGISTRY` у кожній конкретній app) — список dict:
`{'page', 'key', 'type': 'text'|'image'|'bool', 'label', 'default',
'default_en', 'default_ru', 'default_cs', 'multiline'?}`.
`type='bool'` — перемикач видимості секції (ключ зазвичай закінчується
на `_visible`); без i18n-варіантів, зберігається як `'1'`/`'0'` у `value_text`.
"""
from __future__ import annotations

from django import forms
from django.utils.translation import gettext_lazy as _


def get_entry(registry: list[dict], page: str, key: str) -> dict | None:
    for entry in registry:
        if entry['page'] == page and entry['key'] == key:
            return entry
    return None


def build_block_form(registry: list[dict], tenant) -> tuple[forms.Form, dict]:
    """Динамічна форма з полем на кожен запис реєстру. `tenant.blocks` — related manager."""
    fields: dict[str, forms.Field] = {}
    for entry in registry:
        base = f"{entry['page']}__{entry['key']}"
        if entry['type'] == 'image':
            fields[base] = forms.ImageField(required=False, label=str(entry['label']))
        elif entry['type'] == 'bool':
            fields[base] = forms.BooleanField(required=False, label=str(entry['label']))
        else:
            widget = forms.Textarea(attrs={'rows': 3}) if entry.get('multiline') else forms.TextInput
            # Czechia admin: CS + EN only (UA/RU fields remain in DB but are hidden).
            fields[f'{base}__cs'] = forms.CharField(
                required=False, label='Čeština', widget=widget,
            )
            fields[f'{base}__en'] = forms.CharField(
                required=False, label='English', widget=widget,
            )

    form_class = type('TenantBlockForm', (forms.Form,), fields)

    blocks = {f'{b.page}__{b.key}': b for b in tenant.blocks.all()}
    initial: dict[str, object] = {}
    for entry in registry:
        base = f"{entry['page']}__{entry['key']}"
        block = blocks.get(base)
        if not block:
            continue
        if entry['type'] == 'bool':
            initial[base] = block.value_text != '0'
        elif entry['type'] != 'image':
            initial[f'{base}__cs'] = block.value_text_cs or block.value_text
            initial[f'{base}__en'] = block.value_text_en
    return form_class(initial=initial), blocks


def group_blocks_for_template(
    registry: list[dict], page_labels: dict[str, str], form: forms.Form, blocks: dict,
) -> list[dict]:
    """Один запис реєстру = один рядок: bool/image окремо, text — CS+EN разом."""
    groups: dict[str, dict] = {}
    for entry in registry:
        base = f"{entry['page']}__{entry['key']}"
        group = groups.setdefault(
            entry['page'], {'label': page_labels.get(entry['page'], entry['page']), 'fields': []},
        )
        if entry['type'] == 'image':
            block = blocks.get(base)
            group['fields'].append({
                'field': form[base],
                'type': entry['type'],
                'langs': None,
                'current_image': block.value_image if block else None,
            })
        elif entry['type'] == 'bool':
            group['fields'].append({
                'field': form[base],
                'type': entry['type'],
                'langs': None,
            })
        else:
            langs = (
                form[f'{base}__cs'],
                form[f'{base}__en'],
            )
            group['fields'].append({
                'field': langs[0],
                'type': entry['type'],
                'title': str(entry['label']),
                'langs': langs,
            })
    return list(groups.values())


def ensure_registry_blocks(block_model, tenant, registry: list[dict]) -> None:
    """Лінивий seed відсутніх ключів реєстру (нові CTA тощо) без перезапису існуючих."""
    for entry in registry:
        block_model.objects.get_or_create(
            tenant=tenant, page=entry['page'], key=entry['key'],
            defaults={
                'block_type': entry['type'],
                'label': str(entry['label']),
                'value_text': entry.get('default', '') if entry['type'] != 'image' else '',
                'value_text_ru': entry.get('default_ru', ''),
                'value_text_en': entry.get('default_en', ''),
                'value_text_cs': entry.get('default_cs', ''),
            },
        )


# Exact legacy UA/demo placeholders still present after the Czechia fork.
# Only these exact strings are rewritten on seed backfill — never free-form CMS copy.
_KNOWN_UA_LEFTOVERS = frozenset({
    '+38 (063) 952-05-65',
    '+380 67 000 00 00',
    '+380670000000',
    'Kyjev, Tarase Ševčenka 46a',
    'Київ, Тараса Шевченка 46а',
    'Киев, Тараса Шевченко 46а',
})


def backfill_empty_locales(block_model, tenant, registry: list[dict]) -> int:
    """Заповнює порожні *_en/*_cs з default_* реєстру (cs/en).

    Також замінює *точні* UA-заглушки (+38 / Kyjev) у value_text / *_cs / *_en
    на default/default_cs/default_en — без wipe довільного CMS-контенту.
    """
    updated = 0
    for entry in registry:
        if entry.get('type') == 'image':
            continue
        block = block_model.objects.filter(
            tenant=tenant, page=entry['page'], key=entry['key'],
        ).first()
        if block is None:
            continue
        fields = []
        for attr, default_key in (
            ('value_text_en', 'default_en'),
            ('value_text_cs', 'default_cs'),
        ):
            current = getattr(block, attr) or ''
            default = entry.get(default_key) or ''
            if not default:
                continue
            if not current or current.strip() in _KNOWN_UA_LEFTOVERS:
                if current != default:
                    setattr(block, attr, default)
                    fields.append(attr)
        # Primary value_text is CS fallback — fix UA leftovers / empty there too.
        primary_default = entry.get('default') or entry.get('default_cs') or ''
        if primary_default and entry.get('type') != 'bool':
            current = block.value_text or ''
            if not current or current.strip() in _KNOWN_UA_LEFTOVERS:
                if current != primary_default:
                    block.value_text = primary_default
                    fields.append('value_text')
        if fields:
            block.save(update_fields=list(dict.fromkeys(fields)))
            updated += 1
    return updated


def save_blocks(block_model, tenant, registry: list[dict], block_form: forms.Form) -> None:
    for entry in registry:
        name = f"{entry['page']}__{entry['key']}"
        block, _created = block_model.objects.get_or_create(
            tenant=tenant, page=entry['page'], key=entry['key'],
            defaults={'block_type': entry['type'], 'label': str(entry['label'])},
        )
        if entry['type'] == 'image':
            uploaded = block_form.cleaned_data.get(name)
            if uploaded:
                block.value_image = uploaded
                block.save(update_fields=['value_image'])
        elif entry['type'] == 'bool':
            block.value_text = '1' if block_form.cleaned_data.get(name) else '0'
            block.block_type = block_model.BlockType.BOOL
            block.save(update_fields=['value_text', 'block_type'])
        else:
            cs = block_form.cleaned_data.get(f'{name}__cs', '')
            en = block_form.cleaned_data.get(f'{name}__en', '')
            block.value_text_cs = cs
            block.value_text_en = en
            # Keep primary value_text in sync with CS for localized_text fallback.
            block.value_text = cs
            block.save(update_fields=['value_text', 'value_text_en', 'value_text_cs'])
