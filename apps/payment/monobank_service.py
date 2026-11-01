import os
import json
import base64
import logging
from decimal import Decimal
from typing import Optional, Tuple

import requests
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger('payment')

PUB_KEY_CACHE_KEY = 'monobank_pub_key'
PUB_KEY_CACHE_TTL = 60 * 60 * 24


class MonobankAcquiringService:
    BASE_URL = 'https://api.monobank.ua'

    def __init__(self, token: Optional[str] = None, site_url: Optional[str] = None):
        self.token = token or os.getenv('MONOBANK_TOKEN') or getattr(settings, 'MONOBANK_TOKEN', None)
        self.site_url = (site_url or os.getenv('SITE_URL') or getattr(settings, 'SITE_URL', '')).rstrip('/')
        if not self.token:
            logger.error('Monobank token is not configured')

    def _headers(self) -> dict:
        return {
            'X-Token': self.token or '',
            'Content-Type': 'application/json',
        }

    def create_invoice(self, reference: str, amount_uah: Decimal, destination: str, comment: str,
                       validity_seconds: int = 3600) -> Tuple[Optional[str], Optional[str]]:
        logger.warning('Monobank acquiring is disabled on prometeylabs.cz')
        return None, None

    def get_invoice_status(self, invoice_id: str) -> Optional[dict]:
        try:
            url = f'{self.BASE_URL}/api/merchant/invoice/status?invoiceId={invoice_id}'
            resp = requests.get(url, headers=self._headers(), timeout=15)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.exception('Failed to fetch monobank invoice status: %s', e)
            return None

    def get_pub_key(self) -> Optional[bytes]:
        """Fetches and caches the Monobank merchant public key (PEM bytes)."""
        cached = cache.get(PUB_KEY_CACHE_KEY)
        if cached:
            return cached
        if not self.token:
            return None
        try:
            url = f'{self.BASE_URL}/api/merchant/pubkey'
            resp = requests.get(url, headers=self._headers(), timeout=10)
            resp.raise_for_status()
            data = resp.json()
            key_b64 = data.get('key')
            if not key_b64:
                logger.warning('Monobank pubkey response missing "key" field')
                return None
            pem_bytes = base64.b64decode(key_b64)
            cache.set(PUB_KEY_CACHE_KEY, pem_bytes, PUB_KEY_CACHE_TTL)
            return pem_bytes
        except Exception as exc:
            logger.exception('Failed to fetch monobank pubkey: %s', exc)
            return None

    def verify_signature(self, body: bytes, x_sign: Optional[str]) -> bool:
        """
        Verifies Monobank webhook signature.

        Monobank signs the raw request body with ECDSA (secp256r1, SHA-256)
        using the merchant key; the resulting signature is sent in the
        ``X-Sign`` header as base64.

        Returns ``False`` if the signature, key or crypto backend is missing —
        callers must treat ``False`` as "reject the request".
        """
        if not x_sign:
            return False
        try:
            from cryptography.hazmat.primitives import hashes, serialization
            from cryptography.hazmat.primitives.asymmetric import ec
            from cryptography.exceptions import InvalidSignature
        except ImportError:
            logger.error(
                'cryptography package is not installed — Monobank webhook signature '
                'cannot be verified. Install requirements.txt.'
            )
            return False

        pem_bytes = self.get_pub_key()
        if not pem_bytes:
            return False

        try:
            signature = base64.b64decode(x_sign)
            public_key = serialization.load_pem_public_key(pem_bytes)
            if not isinstance(public_key, ec.EllipticCurvePublicKey):
                logger.error('Monobank pubkey is not an EC key')
                return False
            public_key.verify(signature, body, ec.ECDSA(hashes.SHA256()))
            return True
        except InvalidSignature:
            return False
        except Exception as exc:
            logger.exception('Monobank signature verification raised: %s', exc)
            return False
