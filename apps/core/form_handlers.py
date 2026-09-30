"""
Допоміжні функції для обробки форм
"""
import re
import socket
from smtplib import SMTPException, SMTPAuthenticationError, SMTPConnectError
from django.http import JsonResponse
from django.utils import timezone
from django.core.mail import send_mail, get_connection
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# Email timeout (максимум 10 секунд)
EMAIL_TIMEOUT = 10


def validate_phone(phone):
    """Валідація номера телефону — мінімум 7 цифр, будь-який формат."""
    if not phone:
        return False
    digits = re.sub(r'\D', '', phone)
    return len(digits) >= 7


def validate_name(name):
    """Валідація імені - мінімум 2 символи, хоча б одна літера, не тільки цифри"""
    if not name or len(name.strip()) < 2:
        return False
    if name.isdigit():
        return False
    if not any(c.isalpha() for c in name):
        return False
    return True


_EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
_CHECKED = frozenset({'1', 'on', 'true', 'yes'})

LEAD_FORM_TYPES = frozenset({
    'contact',
    'call_request',
    'call-request',
    'footer-consultation',
    'consultation',
    'site-request',
    'site_request',
    'telegram-bot',
    'telegram_bot',
    'developer',
})

_TELEGRAM_RE = re.compile(r'^@?[A-Za-z0-9_]{5,32}$')


def normalize_telegram(value: str) -> str:
    raw = (value or '').strip()
    if not raw:
        return ''
    if raw.startswith('https://t.me/') or raw.startswith('http://t.me/'):
        raw = raw.rstrip('/').rsplit('/', 1)[-1]
    if raw.startswith('@'):
        raw = raw[1:]
    return raw


def validate_telegram(value: str) -> bool:
    raw = normalize_telegram(value)
    if not raw:
        return False
    return bool(_TELEGRAM_RE.match(raw))


def has_lead_contact(phone: str = '', email: str = '', telegram: str = '') -> bool:
    """FAIL-CLOSED: at least one of phone OR email OR telegram."""
    phone_ok = bool(phone and validate_phone(phone))
    email_ok = bool(email and validate_email(email))
    tg_ok = bool(telegram and validate_telegram(telegram))
    # Phone may be prefix-only (+420) — treat as empty via validate_phone digits>=7
    return phone_ok or email_ok or tg_ok


def validate_email(email):
    if not email or not _EMAIL_RE.match(email):
        return False
    return True


def client_ip(request):
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if forwarded:
        return forwarded.split(',')[0].strip() or None
    return request.META.get('REMOTE_ADDR') or None


def has_consent(request) -> bool:
    value = (request.POST.get('consent') or '').strip().lower()
    return value in _CHECKED


def create_form_response(success=True, message="", status=200, **extra_data):
    """Створює стандартну відповідь для AJAX форм"""
    response_data = {
        'success': success,
        'message': message
    }
    response_data.update(extra_data)
    return JsonResponse(response_data, status=status)


def get_form_type_from_path(request):
    """Визначає тип форми на основі URL або інших параметрів"""
    referer = request.META.get('HTTP_REFERER', '')
    if 'calculator' in referer:
        return 'site-request'
    elif 'developer' in referer:
        return 'developer'
    return 'consultation'  # default


def create_form_data(form_type, name, phone, request, **extra_fields):
    """Створює стандартний словник даних для форми"""
    form_data = {
        'type': form_type,
        'name': name,
        'phone': phone,
        'timestamp': timezone.now().strftime('%d.%m.%Y %H:%M'),
        'ip': client_ip(request) or request.META.get('REMOTE_ADDR', ''),
        'user_agent': request.META.get('HTTP_USER_AGENT', ''),
        'gclid': request.POST.get('gclid', '').strip(),
        'utm_source': request.POST.get('utm_source', '').strip(),
        'utm_medium': request.POST.get('utm_medium', '').strip(),
        'utm_campaign': request.POST.get('utm_campaign', '').strip(),
        'utm_term': request.POST.get('utm_term', '').strip(),
        'utm_content': request.POST.get('utm_content', '').strip(),
        'messenger_type': request.POST.get('messenger_type', '').strip(),
        'project_type': request.POST.get('project_type', '').strip(),
        'budget': request.POST.get('budget', '').strip(),
        'preferred_language': request.POST.get('preferred_language', '').strip(),
        'telegram': normalize_telegram(request.POST.get('telegram', '')),
    }
    if has_consent(request):
        form_data['consent_at'] = timezone.now()
        form_data['consent_ip'] = client_ip(request)
    source_page = request.POST.get('source_page', '').strip()
    if source_page:
        form_data['source_page'] = source_page
    landing_page = request.POST.get('landing_page', '').strip()
    if landing_page:
        form_data['landing_page'] = landing_page
    landing_referrer = request.POST.get('landing_referrer', '').strip()
    if landing_referrer:
        form_data['landing_referrer'] = landing_referrer
    form_data.update(extra_fields)
    return form_data


def send_form_email(form_data):
    """Відправка email з даними форми. Повертає (success: bool, error_message: str)"""
    try:
        subject = f"[PrometeyLabs] {form_data['type']}"
        
        # Формуємо тіло email
        message_body = f"""
Нова заявка з сайту PrometeyLabs

Тип заявки: {form_data['type']}
Дата: {form_data['timestamp']}

=== КОНТАКТНІ ДАНІ ===
Ім'я: {form_data['name']}
Телефон: {form_data['phone']}
Email: {form_data.get('email', 'Не вказано')}

=== ДЕТАЛІ ЗАЯВКИ ===
"""
        
        # Додаємо специфічні поля
        for field, value in form_data.items():
            if field not in ['type', 'name', 'phone', 'email', 'timestamp', 'ip', 'user_agent'] and value:
                field_name = {
                    'details': 'Деталі заявки',
                    'message': 'Повідомлення',
                    'course_type': 'Тип курсу',
                    'experience': 'Досвід',
                    'topic': 'Тема консультації',
                    'source_page': 'Сторінка',
                }.get(field, field.replace('_', ' ').title())
                message_body += f"{field_name}: {value}\n"
        
        message_body += f"\n=== ДОДАТКОВА ІНФОРМАЦІЯ ===\nIP: {form_data.get('ip', 'Невідомо')}\nUser Agent: {form_data.get('user_agent', 'Невідомо')}"
        
        # Створюємо connection з timeout
        connection = get_connection(timeout=EMAIL_TIMEOUT)
        
        send_mail(
            subject=subject,
            message=message_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.CONTACT_EMAIL],
            fail_silently=False,
            connection=connection
        )
        
        logger.info(f"Email sent successfully for form type: {form_data['type']}")
        return (True, None)
        
    except (SMTPAuthenticationError, SMTPConnectError) as e:
        error_msg = f"SMTP authentication error: {str(e)}"
        logger.error(error_msg)
        return (False, error_msg)
    except socket.timeout as e:
        error_msg = f"Email timeout (>10 seconds): {str(e)}"
        logger.error(error_msg)
        return (False, error_msg)
    except SMTPException as e:
        error_msg = f"SMTP error: {str(e)}"
        logger.error(error_msg)
        return (False, error_msg)
    except Exception as e:
        error_msg = f"Failed to send email: {str(e)}"
        logger.error(error_msg)
        return (False, error_msg)


def save_form_submission(form_type, form_data, email_success=False):
    """Збереження даних форми в БД. Повертає (success: bool, submission_id, error_message)"""
    try:
        from apps.core.models import FormSubmission
        
        # Основні поля
        submission_data = {
            'form_type': form_type,
            'name': form_data.get('name', ''),
            'phone': form_data.get('phone', ''),
            'email': form_data.get('email', ''),
            'messenger_type': form_data.get('messenger_type', '') or '',
            'project_type': form_data.get('project_type', '') or '',
            'budget': form_data.get('budget', '') or '',
            'preferred_language': form_data.get('preferred_language', '') or '',
            'consent_at': form_data.get('consent_at'),
            'consent_ip': form_data.get('consent_ip'),
            'ip_address': form_data.get('ip'),
            'user_agent': form_data.get('user_agent'),
            'status': 'new',
            'email_sent': email_success,
            'gclid': form_data.get('gclid', ''),
            'utm_source': form_data.get('utm_source', ''),
            'utm_medium': form_data.get('utm_medium', ''),
            'utm_campaign': form_data.get('utm_campaign', ''),
            'utm_term': form_data.get('utm_term', ''),
            'utm_content': form_data.get('utm_content', ''),
        }
        
        if email_success:
            submission_data['email_sent_at'] = timezone.now()
        
        # Деталі (текстові поля)
        detail_fields = ['details', 'message', 'topic']
        for field in detail_fields:
            if form_data.get(field):
                submission_data['details'] = form_data[field]
                break
        
        # Додаткові дані в JSON
        extra_data = {}
        extra_fields = ['course_type', 'experience', 'company', 'answers',
                       'alt_services_checked', 'event_title', 'source_page',
                       'landing_page', 'landing_referrer', 'quiz', 'upsell',
                       'pdf_token', 'telegram', 'bot_task', 'integrations']
        for field in extra_fields:
            if form_data.get(field):
                extra_data[field] = form_data[field]
        
        if extra_data:
            submission_data['extra_data'] = extra_data
        
        submission = FormSubmission.objects.create(**submission_data)
        logger.info(f"Form submission saved: ID {submission.id}, email_sent={email_success}")
        return (True, submission.id, None)
        
    except Exception as e:
        error_msg = f"Failed to save form submission: {str(e)}"
        logger.error(error_msg)
        return (False, None, error_msg)


ANSWER_TEXT_MAP = {
    'question_1': {
        'A': 'Лендінг (одна сторінка)',
        'B': 'Розширений лендінг / промо-сайт (багатосторінковий)',
        'C': 'Корпоративний сайт або сайт послуг',
        'D': 'Інтернет-магазин',
        'E': 'Веб-додаток / PWA'
    },
    'question_2': {
        'A': 'На email',
        'B': 'У месенджер (Telegram / WhatsApp / Viber)',
        'C': 'В адмін-панель сайту (простий кабінет / CRM)',
        'D': 'В існуючу CRM',
        'E': 'Відправка заявок не потрібна'
    },
    'question_3': {
        'A': 'Терміново (3–14 днів)',
        'B': 'Стандартно (7–21 день)',
        'C': 'Не поспішаю (14–28 днів)',
        'D': 'Гнучкий графік, можна підлаштуватися'
    },
    'question_4': {
        'A': 'Ні, оплата на сайті не потрібна',
        'B': 'Так, оплата карткою онлайн',
        'C': 'Так, оплата за рахунком / інвойсом',
        'D': 'Так, кілька способів оплати (картка + рахунок тощо)'
    },
    'question_5': {
        'A': 'Є тільки ідея, потрібна консультація',
        'B': 'Є повне, чітко сформульоване технічне завдання',
        'C': 'Є макети/дизайн',
        'D': 'Є логотип та брендинг',
        'E': 'Є соціальні мережі та контент'
    }
}


def get_answer_text(question, answer):
    """Повертає текст відповіді на основі коду. Підтримує як окремі значення, так і масиви"""
    question_map = ANSWER_TEXT_MAP.get(question, {})
    
    if isinstance(answer, list):
        texts = []
        for ans in answer:
            text = question_map.get(ans, f'Невідома відповідь ({ans})')
            texts.append(text)
        return ', '.join(texts)
    else:
        return question_map.get(answer, f'Невідома відповідь ({answer})')


def send_test_result_email(test_data):
    """Відправка email з результатом тесту - з повними текстами відповідей. Повертає (success: bool, error_message: str)"""
    try:
        name = test_data['name']
        phone = test_data['phone']
        email = (test_data.get('email') or '').strip() or 'Не вказано'
        answers = test_data.get('answers', {})
        alt_services_checked = test_data.get('alt_services_checked', False)
        
        # Перевіряємо, що є для відправки
        has_answers = bool(answers)
        
        # Формуємо рядок з відповідями для email
        answers_text_lines = []
        if has_answers:
            for i in range(1, 6):
                question_key = f'question_{i}'
                if question_key in answers:
                    answer = answers[question_key]
                    answer_text = get_answer_text(question_key, answer)
                    answers_text_lines.append(f"{i}. {answer_text}")
        
        answers_section = '\n'.join(answers_text_lines) if answers_text_lines else ""
        
        # Email для команди
        admin_subject = "[PrometeyLabs] Новий розрахунок проекту"
        admin_message = f"""
Новий розрахунок проекту

=== КОНТАКТ ===
Ім'я: {name}
Телефон: {phone}
Email: {email}

=== ТИП ЗАПИТУ ===
"""
        
        # Додаємо інформацію про тип запиту
        if alt_services_checked and has_answers:
            admin_message += "Галочка: Так (потребує додаткових послуг)\nТест: Пройдений\n"
        elif alt_services_checked:
            admin_message += "Галочка: Так (потребує додаткових послуг)\nТест: Не пройдений\n"
        elif has_answers:
            admin_message += "Галочка: Ні\nТест: Пройдений\n"
        
        # Додаємо відповіді, якщо вони є
        if has_answers:
            admin_message += f"""
=== ВІДПОВІДІ НА ТЕСТ ===
{answers_section}
"""
        
        admin_message += f"""
=== ДОДАТКОВА ІНФОРМАЦІЯ ===
Дата: {timezone.now().strftime('%d.%m.%Y %H:%M')}
IP: {test_data.get('ip', 'Невідомо')}
"""
        
        # Створюємо connection з timeout
        connection = get_connection(timeout=EMAIL_TIMEOUT)
        
        send_mail(
            subject=admin_subject,
            message=admin_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.CONTACT_EMAIL],
            fail_silently=False,
            connection=connection
        )
        
        logger.info(f"Test result emails sent for {name}")
        return (True, None)
        
    except (SMTPAuthenticationError, SMTPConnectError) as e:
        error_msg = f"SMTP authentication error: {str(e)}"
        logger.error(error_msg)
        return (False, error_msg)
    except socket.timeout as e:
        error_msg = f"Email timeout (>10 seconds): {str(e)}"
        logger.error(error_msg)
        return (False, error_msg)
    except SMTPException as e:
        error_msg = f"SMTP error: {str(e)}"
        logger.error(error_msg)
        return (False, error_msg)
    except Exception as e:
        error_msg = f"Failed to send test result email: {str(e)}"
        logger.error(error_msg)
        return (False, error_msg)
