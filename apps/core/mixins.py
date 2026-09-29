"""
Міксини та базові класи для оптимізації коду views
"""
from django.views.generic import TemplateView
from django.utils import timezone
from django.utils import translation

from apps.core.models import Client, PortfolioProject

# Для кожної активної мови (крім базової uk) — впорядкований список
# суфіксів шаблонів-кандидатів, від найбільш специфічного до fallback.
# uk отримує лише базовий `pages/{base}.html` (без суфікса).
LEGAL_TEMPLATE_LANG_FALLBACKS = {
    'cs': ['cs', 'en'],
    'en': ['en'],
}


class BasePageView(TemplateView):
    """Базовий клас для всіх сторінок сайту"""
    page_title = ""
    meta_description = ""
    og_title = ""
    keywords = ""
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': self.page_title,
            'meta_description': self.meta_description,
            'og_title': self.og_title or self.page_title,
            'keywords': self.keywords,
            'current_year': timezone.now().year,
        })
        return context


class LocalizedLegalTemplateMixin:
    """
    Обирає шаблон юридичної сторінки залежно від активної мови інтерфейсу,
    з fallback-ланцюжком (Django `select_template` бере перший наявний файл):

        ru -> pages/{base}-ru.html -> pages/{base}.html (uk)
        cs -> pages/{base}-cs.html -> pages/{base}-en.html -> pages/{base}.html (uk)
        en -> pages/{base}-en.html -> pages/{base}.html (uk)
        uk -> pages/{base}.html

    Підклас повинен визначити `legal_base_name` (напр. `'privacy'`, `'offer'`).
    Поки `*-cs.html`/`*-en.html` не створені (Крок 6), cs/en коректно
    відкатуються на базовий uk-текст замість помилки 500.
    """
    legal_base_name = None

    def get_template_names(self):
        if not self.legal_base_name:
            raise NotImplementedError(
                'LocalizedLegalTemplateMixin потребує legal_base_name у підкласі'
            )
        lang = translation.get_language()
        suffixes = LEGAL_TEMPLATE_LANG_FALLBACKS.get(lang, [])
        candidates = [f'pages/{self.legal_base_name}-{suffix}.html' for suffix in suffixes]
        candidates.append(f'pages/{self.legal_base_name}.html')
        return candidates


def published_portfolio_queryset():
    """Опубліковані проєкти портфоліо."""
    return PortfolioProject.objects.filter(is_published=True)


def portfolio_page_projects():
    projects = list(
        published_portfolio_queryset()
        .filter(show_on_portfolio=True)
        .order_by('order', 'title')
    )
    for index, project in enumerate(projects):
        project.snap_index = index
        project.snap_tone = PortfolioProject.get_snap_tone(index)
        project.snap_layout = project.get_layout_modifier(index)
    return projects


def homepage_clients():
    return Client.objects.filter(is_active=True).order_by('order', 'name')
