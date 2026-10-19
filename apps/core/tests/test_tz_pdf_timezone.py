"""#57: дата в PDF ТЗ — місцевий час Europe/Prague (created_at у UTC)."""
from datetime import datetime, timezone as dt_timezone

from django.conf import settings
from django.test import SimpleTestCase

from apps.core.tz_pdf import TZ_PDF_TIMEZONE, format_tz_created


class TzPdfCreatedTimeTests(SimpleTestCase):
    def test_settings_time_zone_is_prague(self):
        self.assertEqual(settings.TIME_ZONE, 'Europe/Prague')
        self.assertEqual(str(TZ_PDF_TIMEZONE), 'Europe/Prague')

    def test_winter_utc_plus_1(self):
        utc = datetime(2026, 1, 15, 22, 30, tzinfo=dt_timezone.utc)
        self.assertEqual(format_tz_created(utc), '15.01.2026 23:30')

    def test_summer_utc_plus_2_crosses_midnight(self):
        utc = datetime(2026, 7, 31, 22, 30, tzinfo=dt_timezone.utc)
        self.assertEqual(format_tz_created(utc), '01.08.2026 00:30')

    def test_dst_start(self):
        # 29.03.2026: 02:00 CET → 03:00 CEST (01:00 UTC)
        self.assertEqual(format_tz_created(datetime(2026, 3, 29, 0, 59, tzinfo=dt_timezone.utc)), '29.03.2026 01:59')
        self.assertEqual(format_tz_created(datetime(2026, 3, 29, 1, 0, tzinfo=dt_timezone.utc)), '29.03.2026 03:00')

    def test_dst_end(self):
        # 25.10.2026: 03:00 CEST → 02:00 CET (01:00 UTC)
        self.assertEqual(format_tz_created(datetime(2026, 10, 25, 0, 30, tzinfo=dt_timezone.utc)), '25.10.2026 02:30')
        self.assertEqual(format_tz_created(datetime(2026, 10, 25, 1, 30, tzinfo=dt_timezone.utc)), '25.10.2026 02:30')

    def test_naive_treated_as_utc_and_none(self):
        self.assertEqual(format_tz_created(datetime(2026, 7, 1, 10, 0)), '01.07.2026 12:00')
        self.assertEqual(format_tz_created(None), '')

    def test_build_tz_context_uses_prague_time(self):
        from types import SimpleNamespace
        from apps.core.tz_pdf import build_tz_context
        sub = SimpleNamespace(extra_data={}, name='TEST', email='test@example.com', phone='',
                              created_at=datetime(2026, 7, 31, 22, 30, tzinfo=dt_timezone.utc))
        self.assertEqual(build_tz_context(sub)['created'], '01.08.2026 00:30')
