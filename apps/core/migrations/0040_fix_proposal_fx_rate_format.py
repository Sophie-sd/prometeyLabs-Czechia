"""KP Bukáček: ČNB rate shown as '24,340 Kč/€' → Czech format '24,34 Kč/€' (EN: 'CZK 24.34/€').

Idempotent text replace on ProposalSpec bodies; reverse is a no-op.
"""
from django.db import migrations

REPLACEMENTS = (
    ('24,340 Kč/€', '24,34 Kč/€'),
    ('CZK 24.340/€', 'CZK 24.34/€'),
)
FIELDS = ('body', 'body_cs', 'body_en', 'body_ru')


def forwards(apps, schema_editor):
    Spec = apps.get_model('core', 'ProposalSpec')
    for spec in Spec.objects.all():
        changed = []
        for field in FIELDS:
            value = getattr(spec, field, None)
            if not value:
                continue
            new = value
            for old, repl in REPLACEMENTS:
                new = new.replace(old, repl)
            if new != value:
                setattr(spec, field, new)
                changed.append(field)
        if changed:
            spec.save(update_fields=changed)


class Migration(migrations.Migration):
    dependencies = [('core', '0039_client_site_url_and_logo_alt')]
    operations = [migrations.RunPython(forwards, migrations.RunPython.noop)]
