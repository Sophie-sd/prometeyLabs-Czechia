"""Sales-підказки для замовника на вітрині демо-магазину.

Єдине джерело текстів. Не вигадує фічі — лише пояснює те, що вже є на екрані.
"""
from django.utils.translation import gettext_lazy as _

NOTES = (
    {
        'id': 'speed',
        'pages': ('home',),
        'admin_scopes': (),
        'title': _('Сайт не губить рекламу'),
        'body': _(
            'На повільній вітрині людина закриває оголошення, не встигнувши '
            'побачити товар. Тут легкі фото й відкладене завантаження — '
            'без важкого конструктора.'
        ),
    },
    {
        'id': 'mobile',
        'pages': ('home', 'catalog'),
        'admin_scopes': (),
        'title': _('Телефон — окремий кадр'),
        'body': _(
            'У конструкторі телефон — стиснутий комп’ютер. Тут інший перший '
            'екран, кнопки під палець і відступ під виріз iPhone.'
        ),
    },
    {
        'id': 'cms',
        'pages': ('home', 'admin_access'),
        'admin_scopes': ('content',),
        'title': _('Тексти міняєте самі'),
        'body': _(
            'Назва, фото і колір — у вашій адмінці. Зберегли — вітрина вже нова. '
            'Чекати розробника не треба.'
        ),
    },
    {
        'id': 'catalog',
        'pages': ('catalog', 'hits'),
        'admin_scopes': ('product', 'category'),
        'title': _('Каталог замість переписок'),
        'body': _(
            'Покупець шукає товар на сайті, не в месенджері. '
            'Фільтр, пошук і ціна вже тут.'
        ),
    },
    {
        'id': 'pdp_gift',
        'pages': ('product_detail', 'promotions'),
        'admin_scopes': ('product', 'review'),
        'title': _('Акція з картки товару'),
        'body': _(
            'Таймер і подарунок задаєте в товарі. '
            'На вітрині з’являються самі.'
        ),
    },
    {
        'id': 'wishlist',
        'pages': ('wishlist',),
        'admin_scopes': (),
        'title': _('Список бажань без акаунта'),
        'body': _(
            'Гість зберігає товари в браузері. '
            'Після оновлення сторінки список на місці.'
        ),
    },
    {
        'id': 'cart',
        'pages': ('cart',),
        'admin_scopes': (),
        'title': _('Кошик без реєстрації'),
        'body': _(
            'Кількість міняється одразу. '
            'Акаунт для покупки не потрібен.'
        ),
    },
    {
        'id': 'np',
        'pages': ('checkout',),
        'admin_scopes': ('order',),
        'title': _('Doručení ve checkoutu'),
        'body': _(
            'Město a výdejní místo se napovídají. '
            'V demu testovací seznam, v provozu živý adresář dopravce.'
        ),
    },
    {
        'id': 'pay',
        'pages': ('checkout', 'order_success'),
        'admin_scopes': (),
        'title': _('Оплата на ваш рахунок'),
        'body': _(
            'Демо грошей не списує. '
            'У роботі — картка або післяплата на ваш ФОП.'
        ),
    },
    {
        'id': 'orders',
        'pages': ('order_success', 'admin_access'),
        'admin_scopes': ('order',),
        'title': _('Замовлення в одній таблиці'),
        'body': _(
            'Ім’я, телефон, відділення і сума — в адмінці. '
            'Статус змінюєте ви, не в чаті.'
        ),
    },
    {
        'id': 'i18n',
        'pages': ('home', 'admin_access'),
        'admin_scopes': ('content',),
        'title': _('Мови без другої збірки'),
        'body': _(
            'Перемикач мови вже в шапці. '
            'Тексти товарів і кнопок — поля в адмінці.'
        ),
    },
    {
        'id': 'admin',
        'pages': ('admin_access',),
        'admin_scopes': (),
        'title': _('Адмінка лише цього магазину'),
        'body': _(
            'Логін відкриває тільки цей магазин. '
            'Не спільна панель на всіх клієнтів.'
        ),
    },
)

URL_TO_PAGE = {
    'home': 'home',
    'catalog': 'catalog',
    'product_detail': 'product_detail',
    'wishlist': 'wishlist',
    'cart': 'cart',
    'checkout': 'checkout',
    'order_success': 'order_success',
    'hits': 'hits',
    'promotions': 'promotions',
    'admin_access': 'admin_access',
}

ADMIN_MODEL_SCOPE = {
    'shopproduct': 'product',
    'shopcategory': 'category',
    'shopreview': 'review',
    'shoporder': 'order',
}

_NOTES_BY_ID = {note['id']: note for note in NOTES}


def get_note(note_id: str):
    return _NOTES_BY_ID.get(note_id)


def notes_for_page(page: str):
    return [note for note in NOTES if page in note['pages']]


def notes_for_admin_scope(scope: str):
    return [note for note in NOTES if scope in note['admin_scopes']]


def page_from_url_name(url_name: str) -> str:
    return URL_TO_PAGE.get(url_name or '', '')
