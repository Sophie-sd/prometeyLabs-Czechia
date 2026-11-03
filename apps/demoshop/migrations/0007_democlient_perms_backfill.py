"""Ensure DemoClient group permissions exist (RunPython, irreversible backfill)."""
import importlib

from django.db import migrations


def backfill_democlient_permissions(apps, schema_editor):
    """Ensure auth Permissions exist, then assign them to DemoClient group."""
    # Import DEMO_CLIENT_PERMS from 0002
    m0002 = importlib.import_module('apps.demoshop.migrations.0002_democlient_group')
    perms_list = m0002.DEMO_CLIENT_PERMS

    # Ensure permissions exist for demoshop models
    from django.contrib.auth.management import create_permissions
    from django.apps import apps as django_apps
    
    demoshop_app_config = django_apps.get_app_config('demoshop')
    create_permissions(demoshop_app_config, apps=apps, verbosity=0)

    # Get or create DemoClient group and add all permissions
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    
    group, _created = Group.objects.get_or_create(name='DemoClient')
    
    for app_label, codename in perms_list:
        try:
            perm = Permission.objects.get(
                content_type__app_label=app_label,
                codename=codename
            )
            group.permissions.add(perm)
        except Permission.DoesNotExist:
            continue


class Migration(migrations.Migration):

    dependencies = [
        ('demoshop', '0006_shopblock_value_text_cs_shopcategory_name_cs_and_more'),
        ('auth', '__latest__'),
    ]

    operations = [
        migrations.RunPython(
            backfill_democlient_permissions,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
