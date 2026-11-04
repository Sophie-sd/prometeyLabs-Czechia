"""Окремий AdminSite для демо-клієнтів: /demo-admin/

Ізоляція на рівні окремого AdminSite + scoped ModelAdmin + session demo_scope.
Головний /admin/ для демо-юзерів заборонений (is_staff=False).
"""
from django.contrib import admin
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from unfold.sites import UnfoldAdminSite


class DemoAdminSite(UnfoldAdminSite):
    """Окремий admin site тільки для demo ModelAdmin з Unfold UI.
    
    - На /demo-admin/
    - Без auth.User/Group, LogEntry, Proposal, payment, media
    - has_permission = user.is_active + session demo_scope == user.demo_shop + demo.is_active
    - Не потребує is_staff=True
    - Використовує Unfold для однакового UI з головним админом
    """
    
    site_header = _('Demo Shop Administration')
    site_title = _('Demo Admin')
    index_title = _('Manage Your Demo Shop')
    
    def has_permission(self, request: HttpRequest) -> bool:
        """Доступ дозволений якщо:
        - user.is_active
        - session містить demo_scope
        - demo_scope співпадає з user.demo_shop
        - demo shop is_active
        """
        if not request.user.is_active:
            return False
        
        # Перевірка session demo_scope
        demo_scope = request.session.get('demo_scope')
        if not demo_scope:
            return False
        
        demo_type = demo_scope.get('type')
        demo_id = demo_scope.get('id')
        
        if demo_type != 'demoshop':
            return False
        
        # Перевірка user.demo_shop
        try:
            user_shop = request.user.demo_shop
        except AttributeError:
            return False
        
        if not user_shop or user_shop.pk != demo_id:
            return False
        
        # Перевірка is_active демо
        if not user_shop.is_active:
            return False
        
        return True
    
    def get_app_list(self, request, app_label=None):
        """Client-facing naming: the agency's «Демо-магазини» app is *their* shop."""
        app_list = super().get_app_list(request, app_label)
        for app in app_list:
            if app.get('app_label') != 'demoshop':
                continue
            app['name'] = _('Мій магазин')
            for model in app.get('models', []):
                if model.get('object_name') == 'ShopBlock':
                    model['name'] = _('Контент і кольори')
        return app_list

    def login(self, request, extra_context=None):
        """Redirect до home якщо немає прав (не показувати форму логіну)."""
        from django.shortcuts import redirect
        from django.urls import reverse
        
        if not self.has_permission(request):
            return redirect(reverse('home'))
        
        return super().login(request, extra_context)


# Глобальний instance
demo_admin_site = DemoAdminSite(name='demo_admin')
