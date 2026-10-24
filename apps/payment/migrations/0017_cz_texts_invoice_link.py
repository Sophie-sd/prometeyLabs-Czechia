# Data migration (non-destructive, like 0015):
#  * inserts new CMS keys that do not exist yet (pdf_contract_line_nodate);
#  * updates a text ONLY while its DB value still equals the previous default:
#      EN purpose 'under invoice No. … dated' -> bank template 'by the invoice № … from',
#      EN success text -> adds 'We have already received the confirmation.';
#  * fixed-wording keys (doc_invoice / doc_contract / pdf_unit_default) are set to
#    the locked values the code always uses (Faktura/Invoice, Smlouva/Contract,
#    služba/service) — fixes e.g. a «sllužba» typo shown in admin.
# Nothing is deleted; reverse is a no-op.

from django.db import migrations

UPDATES = {
    'purpose_template': {
        'en': (
            'Payment for {service} under invoice No. {number} dated {date}',
            'Payment for {service} by the invoice № {number} from {date}',
        ),
    },
    'success_text': {
        'en': (
            'Payment completed successfully.',
            'Payment completed successfully. We have already received the confirmation.',
        ),
    },
}

LOCKED = {
    'doc_invoice': ('Faktura', 'Invoice'),
    'doc_contract': ('Smlouva', 'Contract'),
    'pdf_unit_default': ('služba', 'service'),
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

    for key, (cs, en) in LOCKED.items():
        PaymentText.objects.filter(key=key).exclude(text_cs=cs).update(text_cs=cs)
        PaymentText.objects.filter(key=key).exclude(text_en=en).update(text_en=en)

    for key in set(UPDATES) | set(LOCKED):
        if key in DEFAULT_TEXTS:
            hint = DEFAULT_TEXTS[key][0]
            PaymentText.objects.filter(key=key).exclude(description=hint).update(description=hint)


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0016_cz_invoice_payment_link'),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
