"""beauty-opt.com.ua is dead (TLS error / HTTP 500): drop the external URL, keep the name. Idempotent."""
from django.db import migrations

DEAD = 'beauty-opt.com.ua'


def forwards(apps, schema_editor):
    for model in ('Client', 'PortfolioProject'):
        Model = apps.get_model('core', model)
        if any(f.name == 'site_url' for f in Model._meta.fields):
            Model.objects.filter(site_url__icontains=DEAD).update(site_url='')


class Migration(migrations.Migration):
    dependencies = [('core', '0040_fix_proposal_fx_rate_format')]
    operations = [migrations.RunPython(forwards, migrations.RunPython.noop)]
