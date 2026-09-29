from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils import timezone
from .mixins import BasePageView, LocalizedLegalTemplateMixin, homepage_clients, portfolio_page_projects
from .form_handlers import (
    validate_phone, validate_name, validate_email, has_consent,
    create_form_response, get_form_type_from_path,
    create_form_data, send_form_email, save_form_submission,
    send_test_result_email, LEAD_FORM_TYPES,
)
from .keycrm_service import sync_submission_to_keycrm
import logging
import threading
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


def _dispatch_async(submission_id, form_data, email_sender=None):
    """
    У фоновому потоці: надсилає email і синхронізує заявку з KeyCRM.

    Робиться після того, як заявку вже збережено в БД. Це звільняє HTTP-відповідь
    від блокувань на SMTP (до 10 с) та KeyCRM API (до 15 с) — користувач бачить
    «Дякуємо» одразу, незалежно від продуктивності зовнішніх сервісів.
    """
    sender = email_sender or send_form_email

    def run():
        from django.db import close_old_connections

        close_old_connections()
        try:
            from apps.core.models import FormSubmission

            email_success, email_error = sender(form_data)
            if not email_success:
                logger.warning(
                    f"Email not sent for submission {submission_id}: {email_error}"
                )

            try:
                submission = FormSubmission.objects.get(id=submission_id)
            except FormSubmission.DoesNotExist:
                logger.error(f"Submission {submission_id} not found in async dispatch")
                return

            if email_success and not submission.email_sent:
                submission.email_sent = True
                submission.email_sent_at = timezone.now()
                submission.save(update_fields=['email_sent', 'email_sent_at'])

            sync_submission_to_keycrm(submission)
        except Exception as e:
            logger.error(f"Async dispatch error for submission {submission_id}: {e}")
        finally:
            close_old_connections()

    threading.Thread(target=run, daemon=True, name=f"submission-{submission_id}").start()


# ===== БАЗОВІ СТОРІНКИ =====

class HomeView(BasePageView):
    template_name = 'pages/home.html'
    page_title = _('PrometeyLabs - Розробка сайтів під ключ | Telegram боти | Реклама')
    meta_description = _('PrometeyLabs - професійна розробка сайтів під ключ, створення Telegram ботів, налаштування реклами Google Ads, навчання веб-розробки. Сучасні технології, конкурентні ціни.')
    og_title = _('PrometeyLabs - Розробка сайтів під ключ')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['home_clients'] = homepage_clients()
        return context


class PortfolioView(BasePageView):
    template_name = 'pages/portfolio.html'
    page_title = _('Портфоліо | Створені нами сайти під ключ - PrometeyLabs')
    meta_description = _('Портфоліо PrometeyLabs - приклади створених сайтів під ключ, Telegram ботів, налаштованої реклами. Подивіться на наші роботи та оцініть якість.')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['portfolio_projects'] = portfolio_page_projects()
        return context


class CalculatorView(BasePageView):
    template_name = 'pages/calculator.html'
    page_title = _('Розрахувати вартість сайту | Калькулятор ціни - PrometeyLabs')
    meta_description = _('Розрахуйте вартість створення сайту онлайн. Сучасні технології знижують ціну розробки. Тест для точного розрахунку вартості проекту.')

class DeveloperView(BasePageView):
    """Landing курсів тимчасово прихований — заявки через developer-modal на інших сторінках."""

    def dispatch(self, request, *args, **kwargs):
        return redirect('home')

class ContactsView(BasePageView):
    template_name = 'pages/contacts.html'
    page_title = _('Контакти | PrometeyLabs - Зв\'яжіться з нами')
    meta_description = _('Зв\'яжіться з командою PrometeyLabs для розробки сайтів, Telegram ботів, реклами чи навчання. Київ, Україна.')

class OfferView(LocalizedLegalTemplateMixin, BasePageView):
    legal_base_name = 'offer'
    page_title = _('Публічний договір (оферта) про надання послуг | PrometeyLabs')
    meta_description = _('Публічний договір (оферта) про надання ІТ-послуг від PrometeyLabs. Офіційні умови надання послуг веб-розробки, мобільних застосунків та маркетингу.')

class PrivacyView(LocalizedLegalTemplateMixin, BasePageView):
    legal_base_name = 'privacy'
    page_title = _('Політика конфіденційності | PrometeyLabs')
    meta_description = _('Політика конфіденційності PrometeyLabs. Дізнайтеся, як ми захищаємо ваші персональні дані відповідно до законодавства України та GDPR.')

class CookiesView(LocalizedLegalTemplateMixin, BasePageView):
    legal_base_name = 'cookies'
    page_title = _('Політика використання файлів cookie | PrometeyLabs')
    meta_description = _('Політика використання файлів cookie від PrometeyLabs. Дізнайтеся, які файли cookie ми використовуємо та як керувати налаштуваннями.')

class RefundPolicyView(LocalizedLegalTemplateMixin, BasePageView):
    legal_base_name = 'refund'
    page_title = _('Політика повернення коштів | PrometeyLabs')
    meta_description = _('Політика повернення коштів від PrometeyLabs. Дізнайтеся про умови і порядок повернення коштів за наші послуги.')

class IntellectualPropertyView(LocalizedLegalTemplateMixin, BasePageView):
    legal_base_name = 'intellectual-property'
    page_title = _('Політика щодо інтелектуальної власності | PrometeyLabs')
    meta_description = _('Політика щодо інтелектуальної власності від PrometeyLabs. Дізнайтеся про права на контент та захист авторських прав.')

class MonobankChastView(BasePageView):
    page_title = 'Покупка частинами monobank | Universal Bank | PrometeyLabs'
    meta_description = 'Юридична інформація щодо послуги Покупка частинами від monobank | Universal Bank.'
    template_name = 'pages/monobank-chastynamy.html'


class InternetShopView(BasePageView):
    """Internet-shop landing (cs default / en prefixed). No RU/UK language paths."""
    template_name = 'pages/internet-shop.html'
    page_title = _('Розробка інтернет-магазинів під ключ | PrometeyLabs')
    meta_description = _('Розробка інтернет-магазинів під ключ від PrometeyLabs. Кастомний код, зручна адмінка, інтеграції з платіжними системами та Новою Поштою. Міграція з Prom, Rozetka.')
    og_title = _('Інтернет-магазини під ключ — PrometeyLabs')


class InternetShopV2View(BasePageView):
    """Нова landing-сторінка інтернет-магазинів (v2) — паралельно до /internet-shop/."""
    template_name = 'pages/internet-shop-v2.html'
    page_title = _('Інтернет-магазини під ключ — швидка розробка e-commerce | PrometeyLabs')
    meta_description = _(
        'Розробка інтернет-магазинів з нативною архітектурою без конструкторів. '
        'Міграція з Prom та OLX, SEO, пожиттєва гарантія на код.'
    )
    og_title = _('Інтернет-магазини, що завантажуються швидше — PrometeyLabs')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['home_clients'] = homepage_clients()
        return context


class CorporateWebsiteV2View(BasePageView):
    """Нова landing-сторінка корпоративних сайтів (v2) — паралельно до /corporate-website/."""
    template_name = 'pages/corporate-website-v2.html'
    page_title = _('Корпоративні сайти та лендінги під ключ — швидка розробка | PrometeyLabs')
    meta_description = _(
        'Розробка корпоративних сайтів та лендінгів з нативною архітектурою. '
        '100/100 Core Web Vitals, технічне SEO, пожиттєва гарантія на код.'
    )
    og_title = _('Корпоративні сайти, що домінують у пошуку — PrometeyLabs')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['home_clients'] = homepage_clients()
        return context


class CorporateWebsiteView(BasePageView):
    """Corporate-website landing (cs default / en prefixed). No RU/UK language paths."""
    template_name = 'pages/corporate-website.html'
    page_title = _('Корпоративний сайт під ключ за 7 днів | Розробка сайту компанії — PrometeyLabs')
    meta_description = _('Створення корпоративного сайту під ключ. Унікальний дизайн, інтеграція з CRM, SEO + реклама Google/Facebook/TikTok у пакеті. Запуск за 7 днів. Команда досвідчених розробників. Розрахуємо вартість у брифі.')
    og_title = _('Корпоративний сайт під ключ — створимо за 7 днів | PrometeyLabs')


class ThankYouView(BasePageView):
    template_name = 'pages/thank_you.html'
    page_title = _('Дякуємо за вашу заявку | PrometeyLabs')
    meta_description = _('Ваша заявка успішно отримана. Ми з вами скоро зв\'яжемось.')


# ===== AJAX ОБРОБКА ФОРМ =====

def handle_form_submission(request):
    """Обробка AJAX форм"""
    if request.method != 'POST':
        return create_form_response(False, _('Метод не дозволений'), status=405)
    
    try:
        # Отримуємо тип форми з data-form-type або окремого поля
        form_type = request.POST.get('form_type') or get_form_type_from_path(request)
        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()

        is_lead = form_type in LEAD_FORM_TYPES

        if is_lead:
            if not has_consent(request):
                return create_form_response(
                    False,
                    _('Підтвердіть згоду на обробку персональних даних.'),
                    status=400,
                )
            email_optional = form_type in {'site_request', 'site-request'}
            if email_optional:
                if email and not validate_email(email):
                    return create_form_response(
                        False,
                        _('Введіть коректний email.'),
                        status=400,
                    )
            elif not email or not validate_email(email):
                return create_form_response(
                    False,
                    _('Введіть коректний email.'),
                    status=400,
                )
            if not name:
                return create_form_response(
                    False,
                    _('Заповніть обов\'язкові поля: ім\'я та email'),
                    status=400,
                )
            if not validate_name(name):
                return create_form_response(
                    False,
                    _('Введіть коректне ім\'я (мінімум 2 символи, хоча б одна літера)'),
                    status=400,
                )
            if phone and not validate_phone(phone):
                return create_form_response(
                    False,
                    _('Введіть коректний номер телефону'),
                    status=400,
                )
        else:
            if not name or not phone:
                return create_form_response(
                    False,
                    _('Заповніть обов\'язкові поля: ім\'я та телефон'),
                )
            if not validate_name(name):
                return create_form_response(
                    False,
                    _('Введіть коректне ім\'я (мінімум 2 символи, хоча б одна літера)'),
                )
            if not validate_phone(phone):
                return create_form_response(
                    False,
                    _('Введіть коректний номер телефону'),
                )
        
        # Обробка різних типів форм
        handlers = {
            'site-request': handle_site_request,
            'site_request': handle_site_request,
            'developer': handle_developer_request,
            'consultation': handle_consultation_request,
            'contact': handle_contact_request,
            'call_request': handle_call_request,
            'footer-consultation': handle_footer_consultation,
        }
        
        handler = handlers.get(form_type)
        if handler:
            return handler(request, name, phone)
        else:
            return create_form_response(
                False,
                _('Невідомий тип форми: {form_type}').format(form_type=form_type),
            )
            
    except Exception as e:
        logger.error(f"Form submission error: {e}")
        return create_form_response(
            False,
            _('Сталася помилка при обробці заявки. Спробуйте ще раз.'),
        )

# Функції get_form_type_from_path та validate_phone перенесені в form_handlers.py

def handle_site_request(request, name, phone):
    """Обробка заявки на сайт"""
    email = request.POST.get('email', '').strip()
    details = request.POST.get('details', '').strip()
    source_page = request.POST.get('source_page', '').strip()

    form_data = create_form_data(
        _('Заявка на розробку сайту'), name, phone, request,
        email=email,
        details=details,
        **(({'source_page': source_page}) if source_page else {}),
    )

    submission_saved, submission_id, save_error = save_form_submission(
        'site-request', form_data, email_success=False
    )

    if not submission_saved:
        logger.error(f"Failed to save site-request submission: {save_error}")
        return create_form_response(False, _('Помилка при збереженні заявки. Спробуйте ще раз.'))

    _dispatch_async(submission_id, form_data)

    return create_form_response(
        True,
        _('Дякуємо! Ваша заявка отримана. Ми зв\'яжемося з вами найближчим часом.'),
        redirect='/thank-you/'
    )

def handle_developer_request(request, name, phone):
    """Обробка заявки на курси"""
    email = request.POST.get('email', '').strip()
    course_type = request.POST.get('course_type', '').strip()
    experience = request.POST.get('experience', '').strip()
    
    form_data = create_form_data(
        _('Заявка на курси програмування'), name, phone, request,
        email=email,
        course_type=course_type,
        experience=experience
    )

    submission_saved, submission_id, save_error = save_form_submission(
        'developer', form_data, email_success=False
    )

    if not submission_saved:
        logger.error(f"Failed to save developer submission: {save_error}")
        return create_form_response(False, _('Помилка при збереженні заявки. Спробуйте ще раз.'))

    _dispatch_async(submission_id, form_data)

    return create_form_response(
        True,
        _('Дякуємо! Ваша заявка на курси отримана. Ми надішлемо детальну інформацію.'),
        redirect='/thank-you/'
    )

def handle_consultation_request(request, name, phone):
    """Обробка заявки на консультацію"""
    email = request.POST.get('email', '').strip()
    topic = request.POST.get('topic', '').strip()
    
    form_data = create_form_data(
        _('Заявка на консультацію'), name, phone, request,
        email=email,
        topic=topic
    )

    submission_saved, submission_id, save_error = save_form_submission(
        'consultation', form_data, email_success=False
    )

    if not submission_saved:
        logger.error(f"Failed to save consultation submission: {save_error}")
        return create_form_response(False, _('Помилка при збереженні заявки. Спробуйте ще раз.'))

    _dispatch_async(submission_id, form_data)

    return create_form_response(
        True,
        _('Дякуємо! Наш спеціаліст зв\'яжеться з вами протягом 15 хвилин.'),
        redirect='/thank-you/'
    )

def handle_contact_request(request, name, phone):
    """Обробка заявки зі сторінки контактів"""
    email = request.POST.get('email', '').strip()
    message = request.POST.get('message', '').strip()
    
    form_data = create_form_data(
        _('Заявка зі сторінки контактів'), name, phone, request,
        email=email,
        message=message
    )

    submission_saved, submission_id, save_error = save_form_submission(
        'contact', form_data, email_success=False
    )

    if not submission_saved:
        logger.error(f"Failed to save contact submission: {save_error}")
        return create_form_response(False, _('Помилка при збереженні заявки. Спробуйте ще раз.'))

    _dispatch_async(submission_id, form_data)

    return create_form_response(
        True,
        _('Дякуємо за ваше повідомлення! Ми зв\'яжемося з вами найближчим часом.'),
        redirect='/thank-you/'
    )



def handle_test_submission(request):
    """Обробка тесту для калькулятора"""
    if request.method != 'POST':
        return create_form_response(False, _('Метод не дозволений'))
    
    try:
        from apps.core.form_handlers import validate_name, validate_phone, validate_email, has_consent
        
        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()

        if not has_consent(request):
            return create_form_response(
                False,
                _('Підтвердіть згоду на обробку персональних даних.'),
                status=400,
            )

        if email and not validate_email(email):
            return create_form_response(
                False,
                _('Введіть коректний email.'),
                status=400,
            )
        
        # Валідація імені та телефону
        if not validate_name(name):
            return create_form_response(False, _('Введіть коректне ім\'я (мінімум 2 символи, хоча б одна літера)'))
        
        if not validate_phone(phone):
            return create_form_response(False, _('Введіть коректний номер телефону (мінімум 10 цифр)'))
        
        # Отримуємо відповіді на тест
        answers = {}
        # Питання 1, 3, 4 - radio (одне значення)
        for i in [1, 3, 4]:
            answer = request.POST.get(f'question_{i}')
            if answer:
                answers[f'question_{i}'] = answer
        
        # Питання 2, 5 - checkbox (масив значень)
        for i in [2, 5]:
            answers_list = request.POST.getlist(f'question_{i}')
            if answers_list:
                answers[f'question_{i}'] = answers_list
        
        # Перевіряємо, чи користувач поставив галочку "alt-services"
        alt_services_checked = request.POST.get('alt-services') == 'on'
        
        # Підготовка даних для email
        test_data = {
            'name': name,
            'phone': phone,
            'email': email,
            'answers': answers,
            'alt_services_checked': alt_services_checked,
            'ip': request.META.get('REMOTE_ADDR', ''),
            'user_agent': request.META.get('HTTP_USER_AGENT', '')
        }
        
        # Підготовка даних для БД
        form_data = create_form_data(
            _('Результат тесту калькулятора'), name, phone, request,
            email=email,
            answers=answers,
            alt_services_checked=alt_services_checked
        )
        
        submission_saved, submission_id, save_error = save_form_submission(
            'test_result', form_data, email_success=False
        )

        if not submission_saved:
            logger.error(f"Failed to save test_result submission: {save_error}")
            return create_form_response(False, _('Помилка при обробці тесту'))

        _dispatch_async(
            submission_id,
            form_data,
            email_sender=lambda _fd, _captured=test_data: send_test_result_email(_captured),
        )

        success_message = _('Дякуємо! Ми зв\'яжемося з вами найближчим часом.')

        return create_form_response(
            True,
            success_message,
            answers=answers,
            alt_services_checked=alt_services_checked,
            redirect='/thank-you/',
        )
        
    except Exception as e:
        logger.error(f"Test submission error: {e}")
        return create_form_response(False, _('Помилка при обробці тесту'))

def handle_call_request(request, name, phone):
    """Обробка заявки на дзвінок"""
    email = request.POST.get('email', '').strip()
    form_data = create_form_data(
        _('Замовлення дзвінка'), name, phone, request,
        email=email,
    )

    submission_saved, submission_id, save_error = save_form_submission(
        'call-request', form_data, email_success=False
    )

    if not submission_saved:
        logger.error(f"Failed to save call-request submission: {save_error}")
        return create_form_response(False, _('Помилка при збереженні заявки. Спробуйте ще раз.'))

    _dispatch_async(submission_id, form_data)

    return create_form_response(
        True,
        _('Дякуємо! Наш менеджер зателефонує вам протягом 15 хвилин.'),
        redirect='/thank-you/'
    )

def handle_footer_consultation(request, name, phone):
    """Обробка заявки з footer форми консультації"""
    email = request.POST.get('email', '').strip()
    form_data = create_form_data(
        _('Заявка з footer - Консультація'), name, phone, request,
        email=email,
    )

    submission_saved, submission_id, save_error = save_form_submission(
        'footer-consultation', form_data, email_success=False
    )

    if not submission_saved:
        logger.error(f"Failed to save footer-consultation submission: {save_error}")
        return create_form_response(False, _('Помилка при збереженні заявки. Спробуйте ще раз.'))

    _dispatch_async(submission_id, form_data)

    return create_form_response(
        True,
        _('Дякуємо! Ми зв\'яжемося з вами найближчим часом.'),
        redirect='/thank-you/'
    )

