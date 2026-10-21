"""
Idempotent: створює повноправного адміністратора (is_staff + is_superuser),
якщо користувача з таким username ще НЕМАЄ. Існуючих користувачів не змінює,
паролі не скидає, нікого не видаляє.

ENV (Render → Environment):
- ENSURE_ADMIN_USERNAME       — username (обов'язково; без нього команда нічого не робить)
- ENSURE_ADMIN_EMAIL          — email (опційно)
- ENSURE_ADMIN_PASSWORD_HASH  — Django password hash (pbkdf2_sha256$…), бажано:
                                у Render зберігається лише хеш, не пароль
- ENSURE_ADMIN_PASSWORD       — або plaintext-пароль (альтернатива хешу)

Пароль/хеш ніколи не комітиться в git і не виводиться в лог.
"""
import os

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import identify_hasher
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Створює superuser з ENV, якщо його ще немає (idempotent, без змін існуючих)'

    def handle(self, *args, **options):
        username = (os.environ.get('ENSURE_ADMIN_USERNAME') or '').strip()
        email = (os.environ.get('ENSURE_ADMIN_EMAIL') or '').strip()
        password_hash = (os.environ.get('ENSURE_ADMIN_PASSWORD_HASH') or '').strip()
        password = os.environ.get('ENSURE_ADMIN_PASSWORD') or ''

        if not username:
            self.stdout.write('ensure_admin: ENSURE_ADMIN_USERNAME not set — skip')
            return
        if not password_hash and not password:
            self.stdout.write('ensure_admin: no ENSURE_ADMIN_PASSWORD_HASH / ENSURE_ADMIN_PASSWORD — skip')
            return
        if password_hash:
            try:
                identify_hasher(password_hash)
            except ValueError:
                self.stdout.write(self.style.ERROR(
                    'ensure_admin: ENSURE_ADMIN_PASSWORD_HASH is not a valid Django hash — skip'
                ))
                return

        User = get_user_model()
        if User.objects.filter(username=username).exists():
            self.stdout.write(f'ensure_admin: user "{username}" already exists — unchanged')
            return

        user = User(username=username, email=email, is_staff=True, is_superuser=True, is_active=True)
        if password_hash:
            user.password = password_hash
        else:
            user.set_password(password)
        user.save()
        self.stdout.write(self.style.SUCCESS(f'ensure_admin: superuser "{username}" created'))
