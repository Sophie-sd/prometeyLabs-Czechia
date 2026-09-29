"""Apply CS+EN blog translations from apps/blog/data (no UK/RU public)."""
from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Alias: runs seed_initial_data (CS+EN from apps/blog/data)'

    def add_arguments(self, parser):
        parser.add_argument('--prune', action='store_true')

    def handle(self, *args, **options):
        call_command('seed_initial_data', prune=options['prune'])
