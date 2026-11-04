"""Logging filters для демо-адмінки: редагування sensitive tokens з логів."""
import re
import logging


class RedactDemoTokenFilter(logging.Filter):
    """Фільтр що маскує kp_token з URL /demo/<slug>/open/<token>/ в логах.
    
    Приклад:
        "GET /demo/test-shop/open/eyJk...abc123:xyz789/" → 
        "GET /demo/test-shop/open/[REDACTED]/"
    """
    
    # Regex для URL з довгим kp_token (мінімум 20 символів, підтримує Django signing format)
    # Формат токена: base64:timestamp:signature (з :, {, }, та різними символами)
    TOKEN_PATTERN = re.compile(
        r'/demo/([^/]+)/open/([^/\s]{20,})/'
    )
    
    def filter(self, record):
        """Редагує token з record.getMessage()."""
        if hasattr(record, 'msg') and record.msg:
            # Замінюємо токен на [REDACTED]
            record.msg = self.TOKEN_PATTERN.sub(
                r'/demo/\1/open/[REDACTED]/',
                str(record.msg)
            )
        
        # Також перевіряємо args (якщо msg містить %s placeholders)
        if hasattr(record, 'args') and record.args:
            if isinstance(record.args, tuple):
                record.args = tuple(
                    self.TOKEN_PATTERN.sub(r'/demo/\1/open/[REDACTED]/', str(arg))
                    if isinstance(arg, str) else arg
                    for arg in record.args
                )
            elif isinstance(record.args, dict):
                record.args = {
                    k: self.TOKEN_PATTERN.sub(r'/demo/\1/open/[REDACTED]/', str(v))
                    if isinstance(v, str) else v
                    for k, v in record.args.items()
                }
        
        return True
