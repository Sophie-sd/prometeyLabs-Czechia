from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.db import migrations

from apps.core.portfolio_seed_data import HOME_CLIENTS


def seed_clients_forward(apps, schema_editor):
    """Same rows as the seed_clients command, but through the historical model.

    The command works on the live model, so every field added later (site_url in
    0039) would make this migration query a column the table does not have yet.
    """
    Client = apps.get_model('core', 'Client')
    static_root = Path(settings.BASE_DIR) / 'static'

    for item in HOME_CLIENTS:
        client, created = Client.objects.get_or_create(
            name=item['name'].strip(),
            defaults={'order': item.get('order', 0), 'is_active': True},
        )
        if not created:
            client.order = item.get('order', 0)
            client.is_active = True

        rel_path = item.get('static_home') or ''
        full_path = static_root / rel_path if rel_path else None
        if full_path is not None and full_path.is_file() and not client.logo:
            with full_path.open('rb') as handle:
                client.logo.save(full_path.name, File(handle), save=False)
        client.save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_client'),
    ]

    operations = [
        migrations.RunPython(seed_clients_forward, migrations.RunPython.noop),
    ]
