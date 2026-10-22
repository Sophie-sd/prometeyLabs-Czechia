# Data migration after the design review (non-destructive):
#  * inserts new CMS text keys that do not exist yet (questions link, short
#    method names for copy buttons, signature caption);
#  * updates a text ONLY while its DB value still equals the previous default
#    (EN 'Executor' -> 'Supplier', purpose 'by the invoice № … from' ->
#    'under invoice No. … dated', copy button labels). Texts edited by the
#    owner are left untouched. Nothing is deleted; reverse is a no-op.

from django.db import migrations

# key -> {lang: (previous default, new default)}
UPDATES = {
    'executor_label': {'en': ('Executor', 'Supplier')},
    'pdf_executor': {'en': ('Executor', 'Supplier')},
    'pdf_signature': {'en': ('Executor', 'Supplier')},
    'copy_details': {
        'cs': ('Kopírovat platební údaje', 'Kopírovat údaje {method}'),
        'en': ('Copy payment details', 'Copy {method} details'),
    },
    'copied': {
        'cs': ('✓ Zkopírováno', 'Zkopírováno ✓'),
        'en': ('✓ Copied', 'Copied ✓'),
    },
    'purpose_template': {
        'en': (
            'Payment for {service} by the invoice № {number} from {date}',
            'Payment for {service} under invoice No. {number} dated {date}',
        ),
    },
}


def forwards(apps, schema_editor):
    from apps.payment.texts import DEFAULT_TEXTS

    PaymentText = apps.get_model('payment', 'PaymentText')

    existing = set(PaymentText.objects.values_list('key', flat=True))
    PaymentText.objects.bulk_create([
        PaymentText(key=key, description=hint, text_cs=cs, text_en=en)
        for key, (hint, cs, en) in DEFAULT_TEXTS.items()
        if key not in existing
    ])

    for key, langs in UPDATES.items():
        for lang, (old, new) in langs.items():
            field = 'text_en' if lang == 'en' else 'text_cs'
            PaymentText.objects.filter(key=key, **{field: old}).update(**{field: new})
        if key in DEFAULT_TEXTS:
            hint = DEFAULT_TEXTS[key][0]
            PaymentText.objects.filter(key=key).exclude(description=hint).update(description=hint)


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0014_cz_seed_payment_texts_and_settings'),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
