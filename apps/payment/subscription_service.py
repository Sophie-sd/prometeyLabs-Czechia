import json
import logging
from decimal import Decimal
from typing import Optional, Tuple

import requests
from django.conf import settings as django_settings

from .monobank_service import MonobankAcquiringService

logger = logging.getLogger('payment')


class MonobankSubscriptionService(MonobankAcquiringService):
    """
    Extends MonobankAcquiringService with Wallet API methods for recurring billing.

    First payment: create_invoice_with_save_card() — client pays and card is saved.
    Subsequent payments: charge_wallet() — merchant charges saved card silently.
    """

    def __init__(self, token: Optional[str] = None, site_url: Optional[str] = None):
        sub_token = (
            token
            or getattr(django_settings, 'MONOBANK_SUBSCRIPTION_TOKEN', None)
            or None
        )
        super().__init__(token=sub_token, site_url=site_url)

    def create_invoice_with_save_card(
        self,
        reference: str,
        wallet_id: str,
        amount_uah: Decimal,
        destination: str,
        comment: str,
        validity_seconds: int = 3600,
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Creates a Monobank invoice with saveCardData so the client's card
        is stored after successful payment.

        Returns (invoiceId, pageUrl) or (None, None) on failure.
        """
        logger.warning('Monobank subscriptions are disabled on prometeylabs.cz')
        return None, None

    def charge_wallet(
        self,
        card_token: str,
        wallet_id: str,
        amount_uah: Decimal,
        reference: str,
        destination: str,
        comment: str,
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Charges a saved card via Monobank Wallet API.
        POST /api/merchant/wallet/payment

        Returns (invoiceId, status) or (None, None) on error.
        Possible statuses: 'success', 'processing', 'created', 'failure'.
        """
        logger.warning('Monobank wallet charge is disabled on prometeylabs.cz')
        return None, None

    def get_wallet_cards(self, wallet_id: str) -> Optional[list]:
        """Returns a list of saved cards for the given walletId."""
        try:
            url = f'{self.BASE_URL}/api/merchant/wallet?walletId={wallet_id}'
            resp = requests.get(url, headers=self._headers(), timeout=15)
            resp.raise_for_status()
            return resp.json()
        except Exception as exc:
            logger.exception('Failed to get wallet cards: %s', exc)
            return None
