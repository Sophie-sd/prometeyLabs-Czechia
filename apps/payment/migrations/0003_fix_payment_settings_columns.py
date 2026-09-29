# Historical no-op: PaymentSettings columns already created in 0001_initial.
# Kept for migration graph continuity (was Postgres ADD COLUMN IF NOT EXISTS).

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0002_paymentlink_contract_file'),
    ]

    operations = []
