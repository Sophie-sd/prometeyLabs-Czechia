"""Тести для logging filter що редагує demo tokens."""
import logging
from django.test import TestCase

from apps.demoshop.logging_filters import RedactDemoTokenFilter


class RedactDemoTokenFilterTests(TestCase):
    """Тести для RedactDemoTokenFilter."""
    
    def test_filter_redacts_kp_token_from_log_message(self):
        """Фільтр маскує kp_token з повідомлення логу."""
        filter_instance = RedactDemoTokenFilter()
        
        # Створюємо LogRecord з URL що містить токен
        record = logging.LogRecord(
            name='django.request',
            level=logging.WARNING,
            pathname='',
            lineno=0,
            msg='Too Many Requests: /demo/test-shop/open/{"demo_id":1}:1xOHKx:AbCdEfG123456789/',
            args=(),
            exc_info=None
        )
        
        # Застосовуємо фільтр
        filter_instance.filter(record)
        
        # Перевіряємо що токен замаскований
        self.assertIn('[REDACTED]', record.msg)
        self.assertNotIn('AbCdEfG123456789', record.msg)
        self.assertEqual(
            record.msg,
            'Too Many Requests: /demo/test-shop/open/[REDACTED]/'
        )
    
    def test_filter_redacts_token_with_special_chars(self):
        """Фільтр працює з токенами що містять спеціальні символи."""
        filter_instance = RedactDemoTokenFilter()
        
        record = logging.LogRecord(
            name='django.request',
            level=logging.WARNING,
            pathname='',
            lineno=0,
            msg='Not Found: /demo/shop-slug/open/eyJkZW1vX2lkIjoxfQ:1xOHKx:Z66og9kp_NBklwhgoou57DlLe0o1Mwaf0ZywTwcZhfY/',
            args=(),
            exc_info=None
        )
        
        filter_instance.filter(record)
        
        self.assertIn('[REDACTED]', record.msg)
        self.assertEqual(
            record.msg,
            'Not Found: /demo/shop-slug/open/[REDACTED]/'
        )
    
    def test_filter_preserves_other_urls(self):
        """Фільтр не змінює інші URL."""
        filter_instance = RedactDemoTokenFilter()
        
        record = logging.LogRecord(
            name='django.request',
            level=logging.INFO,
            pathname='',
            lineno=0,
            msg='GET /proposal/test/ HTTP/1.1',
            args=(),
            exc_info=None
        )
        
        original_msg = record.msg
        filter_instance.filter(record)
        
        # Повідомлення має залишитися незмінним
        self.assertEqual(record.msg, original_msg)
    
    def test_filter_with_short_token_no_redaction(self):
        """Фільтр не чіпає короткі строки (< 20 символів)."""
        filter_instance = RedactDemoTokenFilter()
        
        record = logging.LogRecord(
            name='django.request',
            level=logging.WARNING,
            pathname='',
            lineno=0,
            msg='GET /demo/shop/open/short/',
            args=(),
            exc_info=None
        )
        
        original_msg = record.msg
        filter_instance.filter(record)
        
        # Короткий "токен" не має бути замаскований (це не токен)
        self.assertEqual(record.msg, original_msg)
