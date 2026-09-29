# SQLite-safe AddField (was Postgres ADD COLUMN IF NOT EXISTS).

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0003_fix_payment_settings_columns'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentlink',
            name='company_info',
            field=models.TextField(blank=True, default=''),
        ),
    ]
