"""
Idempotent-команда для надання staff-доступу до операційних розділів адмінки.

Надає доступ до CRM, платежів, сайту та блогу без superuser і без керування
користувачами.

ENV:
- DJANGO_STAFF_ADMIN_USERNAME (дефолт: ValeriaKornienko)

Приклад:
    python manage.py grant_staff_admin_access
    python manage.py grant_staff_admin_access --username ValeriaKornienko
"""
import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apps.core.admin_permissions import (
    STAFF_ADMIN_USERNAME,
    get_staff_admin_permissions,
)


class Command(BaseCommand):
    help = (
        'Надає staff-доступ до операційних розділів адмінки '
        '(CRM, платежі, сайт, блог) без superuser.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Username користувача для надання доступу',
        )

    def handle(self, *args, **options):
        User = get_user_model()
        username = options.get('username') or os.environ.get(
            'DJANGO_STAFF_ADMIN_USERNAME',
            STAFF_ADMIN_USERNAME,
        )

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # Soft-skip on fresh deploys: staff user may not exist until created
            # manually or via a separate seed. Hard-fail would block Render builds.
            self.stdout.write(
                self.style.WARNING(
                    f'⚠️  Користувач "{username}" не знайдений — '
                    'пропускаємо grant_staff_admin_access (не фатально для деплою).'
                )
            )
            return

        staff_permissions = get_staff_admin_permissions()

        user.is_staff = True
        user.is_superuser = False
        user.is_active = True
        user.save(update_fields=['is_staff', 'is_superuser', 'is_active'])

        user.user_permissions.set(staff_permissions)

        perm_count = staff_permissions.count()
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Staff-доступ надано користувачу "{username}":\n'
                f'   is_staff=True, is_superuser=False\n'
                f'   Призначено {perm_count} permissions (core, blog, payment)'
            )
        )
