"""Security: legacy demo owners (provisioned before the DemoAdminSite) were is_staff=True
with a usable password and could open the main /admin/. Make them non-staff with an
unusable password. Updates only; deletes nothing. Reverse is a no-op."""
from django.contrib.auth.hashers import make_password
from django.db import migrations


def harden_demo_users(apps, schema_editor):
    DemoShop = apps.get_model('demoshop', 'DemoShop')
    User = apps.get_model('auth', 'User')
    ids = DemoShop.objects.exclude(owner_user=None).values_list('owner_user_id', flat=True)
    for u in User.objects.filter(pk__in=list(ids), is_superuser=False):
        u.is_staff = False
        u.password = make_password(None)  # unusable
        u.save(update_fields=['is_staff', 'password'])


class Migration(migrations.Migration):
    dependencies = [('demoshop', '0008_add_demo_login_token'), ('auth', '__latest__')]
    operations = [migrations.RunPython(harden_demo_users, migrations.RunPython.noop)]
