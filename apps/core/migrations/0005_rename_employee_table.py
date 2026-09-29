# Migration to rename the Employee table from core_employee to auth_employee
# Idempotent: on fresh DBs 0004 already creates auth_employee (db_table), so
# core_employee may not exist — skip rename in that case.

from django.db import migrations


def rename_employee_table(apps, schema_editor):
    connection = schema_editor.connection
    with connection.cursor() as cursor:
        existing = connection.introspection.table_names(cursor)
    if 'core_employee' in existing and 'auth_employee' not in existing:
        schema_editor.execute('ALTER TABLE core_employee RENAME TO auth_employee;')


def reverse_rename_employee_table(apps, schema_editor):
    connection = schema_editor.connection
    with connection.cursor() as cursor:
        existing = connection.introspection.table_names(cursor)
    if 'auth_employee' in existing and 'core_employee' not in existing:
        schema_editor.execute('ALTER TABLE auth_employee RENAME TO core_employee;')


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_employee'),
    ]

    operations = [
        migrations.RunPython(rename_employee_table, reverse_rename_employee_table),
    ]
