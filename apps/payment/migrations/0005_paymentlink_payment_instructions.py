# SQLite-safe AddField (was Postgres ADD COLUMN IF NOT EXISTS).

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0004_paymentlink_company_info'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentlink',
            name='payment_instructions',
            field=models.TextField(blank=True, default=''),
        ),
    ]
