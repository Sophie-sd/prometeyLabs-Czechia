# Data migration (insert-only, non-destructive):
#  * seeds editable CMS texts for the .cz payment page / invoice PDF (missing keys only);
#  * creates the PaymentSettings singleton if it does not exist yet, so the
#    executor block («FOP Dmytrenko Sofiia») is editable in admin.
# Existing rows are never modified. Reverse is a no-op (nothing is deleted).

from django.db import migrations


def seed(apps, schema_editor):
    from apps.payment.texts import DEFAULT_TEXTS

    PaymentText = apps.get_model('payment', 'PaymentText')
    existing = set(PaymentText.objects.values_list('key', flat=True))
    PaymentText.objects.bulk_create([
        PaymentText(key=key, description=hint, text_cs=cs, text_en=en)
        for key, (hint, cs, en) in DEFAULT_TEXTS.items()
        if key not in existing
    ])

    PaymentSettings = apps.get_model('payment', 'PaymentSettings')
    if not PaymentSettings.objects.exists():
        PaymentSettings.objects.create()


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0013_cz_payment_methods_invoices_eu'),
    ]

    operations = [
        migrations.RunPython(seed, migrations.RunPython.noop),
    ]
