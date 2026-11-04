"""Hide (never delete) home-strip clients that have no live site (Oleg, 04.11.2026)."""
from django.db import migrations

NAMES = ('Coresync', 'Adiabatic', 'RedRabbit', 'Pulvas Store')


def hide(apps, schema_editor):
    apps.get_model('core', 'Client').objects.filter(name__in=NAMES).update(is_active=False)


def show(apps, schema_editor):
    apps.get_model('core', 'Client').objects.filter(name__in=NAMES).update(is_active=True)


class Migration(migrations.Migration):
    dependencies = [('core', '0039_client_site_url_and_logo_alt')]
    operations = [migrations.RunPython(hide, show)]
