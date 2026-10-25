"""Cookie consent audit trail (GDPR čl. 7 odst. 1 — ability to demonstrate consent).

One row per explicit banner choice. No IP address is stored; the random
`consent_id` also lives in the visitor's first-party `pl_consent` cookie, so a
record can be matched to a browser on request.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _


class ConsentLog(models.Model):
    ACTION_CHOICES = [
        ('accept_all', 'accept_all'),
        ('reject_all', 'reject_all'),
        ('custom', 'custom'),
        ('migrated', 'migrated'),
    ]

    consent_id = models.CharField(_('ID souhlasu'), max_length=40, db_index=True)
    action = models.CharField(_('Дія'), max_length=16, choices=ACTION_CHOICES)
    analytics = models.BooleanField(_('Analytics'), default=False)
    marketing = models.BooleanField(_('Marketing'), default=False)
    policy_version = models.PositiveSmallIntegerField(_('Версія'), default=1)
    language = models.CharField(_('Мова'), max_length=8, blank=True)
    path = models.CharField(_('Сторінка'), max_length=200, blank=True)
    user_agent = models.CharField(_('User-Agent'), max_length=200, blank=True)
    created_at = models.DateTimeField(_('Створено'), auto_now_add=True, db_index=True)

    class Meta:
        app_label = 'core'
        verbose_name = _('Згода cookie')
        verbose_name_plural = _('Згоди cookie')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.consent_id} {self.action} a={int(self.analytics)} m={int(self.marketing)}'
