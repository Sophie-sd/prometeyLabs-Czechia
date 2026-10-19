"""Поточні 12 проєктів портфоліо (частина 1)."""

PORTFOLIO_PROJECTS_1 = [
    {
        'slug': 'znomax',
        'title': 'ZNOMax',
        'subtitle': 'ПІДГОТОВКА ДО НМТ',
        'title_ru': 'ZNOMax',
        'subtitle_ru': 'ПОДГОТОВКА К НМТ',
        'card_description': (
            'Освітня онлайн-платформа підготовки до НМТ: короткі відеоуроки, практичні тести, '
            'шпаргалки та підтримка учнів у форматі підписки.'
        ),
        'card_description_ru': (
            'Образовательная онлайн-платформа подготовки к НМТ: короткие видеоуроки, практические '
            'тесты, шпаргалки и поддержка учеников в формате подписки.'
        ),
        'integrations': (
            'відеокурси та тести\n'
            'підписка та оплати\n'
            'особистий кабінет учня\n'
            'мультипредметна база завдань'
        ),
        'card_image_alt': 'ZNOMax — підготовка до НМТ',
        'card_image_alt_ru': 'ZNOMax — подготовка к НМТ',
        'site_url': 'https://znomax.online/',
        'capture_locale': 'uk-UA',
        'static_card': 'images/portfolio/screens/znomax-desktop.webp',
        'static_card_mobile': 'images/portfolio/screens/znomax-mobile.webp',
        'order': 40,
        'home_order': 99,
        'show_on_portfolio': True,
        'show_on_homepage': False,
    },
    {
        'slug': 'ucvn',
        'title': 'UCVN',
        'subtitle': 'VETERINARY NUTRITION COLLEGE',
        'title_ru': 'UCVN',
        'subtitle_ru': 'ВЕТЕРИНАРНАЯ ДИЕТОЛОГИЯ',
        'card_description': (
            'Сайт приватного коледжу доказової ветеринарної дієтології: освітні програми, '
            'сертифікація фахівців і матеріали для ветеринарів.'
        ),
        'card_description_ru': (
            'Сайт частного колледжа доказательной ветеринарной диетологии: образовательные '
            'программы, сертификация специалистов и материалы для ветеринаров.'
        ),
        'integrations': (
            'каталог курсів\n'
            'заявка на навчання\n'
            'сертифікація\n'
            'мультимовний контент'
        ),
        'card_image_alt': 'UCVN — Ukrainian College of Veterinary Nutrition',
        'card_image_alt_ru': 'UCVN — колледж ветеринарной диетологии',
        'site_url': 'https://ucvn.com.ua/',
        'capture_locale': 'uk-UA',
        'static_card': 'images/portfolio/screens/ucvn-desktop.webp',
        'static_card_mobile': 'images/portfolio/screens/ucvn-mobile.webp',
        'order': 1,
        'home_order': 99,
        'show_on_portfolio': True,
        'show_on_homepage': False,
    },
    {
        'slug': 'fpsu',
        'title': 'Федерація Професійних Спілок України',
        'subtitle': 'ПРОФСПІЛКИ',
        'title_ru': 'Федерация Профессиональных Союзов Украины',
        'subtitle_ru': 'ПРОФСОЮЗЫ',
        'card_description': (
            'Офіційний сайт Федерації професійних спілок України: захист прав працівників, безпека '
            'праці, новини соціального діалогу та структура організації.'
        ),
        'card_description_ru': (
            'Официальный сайт Федерации профессиональных союзов Украины: защита прав работников, '
            'безопасность труда, новости социального диалога и структура организации.'
        ),
        'integrations': (
            'новинна стрічка\n'
            'структура регіональних осередків\n'
            'документи та правові матеріали\n'
            'мультимовність'
        ),
        'card_image_alt': 'Федерація Професійних Спілок України — профспілки',
        'card_image_alt_ru': 'Федерация Профессиональных Союзов Украины — профсоюзы',
        'site_url': 'https://www.fpsu.org.ua/',
        'capture_locale': 'uk-UA',
        'static_card': 'images/portfolio/screens/fpsu-desktop.webp',
        'static_card_mobile': 'images/portfolio/screens/fpsu-mobile.webp',
        'order': 39,
        'home_order': 99,
        'show_on_portfolio': True,
        'show_on_homepage': False,
    },
    {
        'slug': 'kvest-marafon',
        'title': 'Квест-марафон',
        'subtitle': 'QUEST ROOMS',
        'title_ru': 'Квест-марафон',
        'subtitle_ru': 'КВЕСТ-РУМЫ',
        'card_description': (
            'Сайт мережі квест-кімнат: п’ять кімнат, п’ять загадок — один маршрут без розвилок. '
            'Онлайн-бронювання сеансів та опис кожної локації.'
        ),
        'card_description_ru': (
            'Сайт сети квест-комнат: пять комнат, пять загадок — один маршрут без развилок. '
            'Онлайн-бронирование сеансов и описание каждой локации.'
        ),
        'integrations': (
            'онлайн-бронювання сеансів\n'
            'календар вільних слотів\n'
            'опис локацій\n'
            'форма зворотного зв’язку'
        ),
        'card_image_alt': 'Квест-марафон — квест-кімнати',
        'card_image_alt_ru': 'Квест-марафон — квест-комнаты',
        'site_url': 'https://www.kvest-marafon.com/',
        'capture_paths': ['about/', 'contacts/', 'faq/'],
        'capture_locale': 'uk-UA',
        'static_card': 'images/portfolio/screens/kvest-marafon-desktop.webp',
        'static_card_mobile': 'images/portfolio/screens/kvest-marafon-mobile.webp',
        'order': 90,
        'home_order': 99,
        'show_on_portfolio': False,
        'show_on_homepage': False,
    },
    {
        'slug': 'ofion',
        'title': 'OFION',
        'subtitle': 'ЕЛІТНІ ПОДАРУНКИ',
        'title_ru': 'OFION',
        'subtitle_ru': 'ЭЛИТНЫЕ ПОДАРКИ',
        'card_description': (
            'Інтернет-магазин елітних подарунків преміум-класу: книги у шкіряній палітурці, '
            'VIP-набори, статуетки та ексклюзивний декор.'
        ),
        'card_description_ru': (
            'Интернет-магазин элитных подарков премиум-класса: книги в кожаном переплёте, '
            'VIP-наборы, статуэтки и эксклюзивный декор.'
        ),
        'integrations': (
            'каталог товарів\n'
            'онлайн-оплата\n'
            'кошик і оформлення замовлення\n'
            'галерея товару'
        ),
        'card_image_alt': 'OFION — елітні подарунки преміум класу',
        'card_image_alt_ru': 'OFION — элитные подарки премиум класса',
        'site_url': 'https://ofion.com.ua/',
        'capture_locale': 'uk-UA',
        'static_card': 'images/portfolio/screens/ofion-desktop.webp',
        'static_card_mobile': 'images/portfolio/screens/ofion-mobile.webp',
        'order': 4,
        'home_order': 99,
        'show_on_portfolio': True,
        'show_on_homepage': False,
    },
    {
        'slug': 'zatyshnyi-dvir',
        'title': 'Затишний двір',
        'subtitle': 'ТОВАРИ ДЛЯ ДОМУ ТА САДУ',
        'title_ru': 'Затишний двір',
        'subtitle_ru': 'ТОВАРЫ ДЛЯ ДОМА И САДА',
        'card_description': (
            'Інтернет-магазин товарів для дому, саду та затишку: каталог продукції з швидким '
            'оформленням замовлення і доставкою по Україні.'
        ),
        'card_description_ru': (
            'Интернет-магазин товаров для дома, сада и уюта: каталог продукции с быстрым '
            'оформлением заказа и доставкой по Украине.'
        ),
        'integrations': (
            'каталог товарів\n'
            'кошик і оформлення замовлення\n'
            'доставка Новою поштою\n'
            'онлайн-оплата'
        ),
        'card_image_alt': 'Затишний двір — товари для дому та саду',
        'card_image_alt_ru': 'Затишний двір — товары для дома и сада',
        'site_url': 'https://zatyshnyidvir.com/',
        'capture_locale': 'uk-UA',
        'static_card': 'images/portfolio/screens/zatyshnyi-dvir-desktop.webp',
        'static_card_mobile': 'images/portfolio/screens/zatyshnyi-dvir-mobile.webp',
        'order': 91,
        'home_order': 99,
        'show_on_portfolio': False,
        'show_on_homepage': False,
    },
    {
        'slug': 'droproom',
        'title': 'DropRoom',
        'subtitle': 'АУТЛЕТ-БРЕНДИ',
        'title_ru': 'DropRoom',
        'subtitle_ru': 'АУТЛЕТ-БРЕНДЫ',
        'card_description': (
            'Інтернет-магазин оригінальних брендів з аутлетів Європи та США: ціни нижчі за '
            'роздрібні завдяки аутлетним колекціям та залишкам брендів.'
        ),
        'card_description_ru': (
            'Интернет-магазин оригинальных брендов из аутлетов Европы и США: цены ниже '
            'розничных благодаря аутлетным коллекциям и остаткам брендов.'
        ),
        'integrations': (
            'каталог з фільтрами\n'
            'кошик і оформлення замовлення\n'
            'онлайн-оплата\n'
            'доставка по Україні'
        ),
        'card_image_alt': 'DropRoom — оригінальні бренди з аутлетів',
        'card_image_alt_ru': 'DropRoom — оригинальные бренды из аутлетов',
        'site_url': 'https://droproom.com.ua/',
        'capture_locale': 'uk-UA',
        'static_card': 'images/portfolio/screens/droproom-desktop.webp',
        'static_card_mobile': 'images/portfolio/screens/droproom-mobile.webp',
        'order': 5,
        'home_order': 99,
        'show_on_portfolio': True,
        'show_on_homepage': False,
    },
    {
        'slug': 'vezhi-rozhnovskogo',
        'title': 'Укркотлобуд',
        'subtitle': 'ВЕЖІ РОЖНОВСЬКОГО ТА КОТЛИ',
        'title_ru': 'Укркотлобуд',
        'subtitle_ru': 'БАШНИ РОЖНОВСКОГО И КОТЛЫ',
        'card_description': (
            'Корпоративний сайт виробника водонапірних башт Рожновського та парових і водогрійних '
            'котлів: каталог продукції, монтаж під ключ, доставка по всій Україні.'
        ),
        'card_description_ru': (
            'Корпоративный сайт производителя водонапорных башен Рожновского и паровых/водогрейных '
            'котлов: каталог продукции, монтаж под ключ, доставка по всей Украине.'
        ),
        'integrations': (
            'каталог продукції\n'
            'заявка на прорахунок\n'
            'галерея реалізованих проєктів\n'
            'контакти виробництва'
        ),
        'card_image_alt': 'Укркотлобуд — вежі Рожновського та котли',
        'card_image_alt_ru': 'Укркотлобуд — башни Рожновского и котлы',
        'site_url': 'https://vezhi-rozhnovskogo.com.ua/',
        'capture_locale': 'uk-UA',
        'static_card': 'images/portfolio/screens/vezhi-rozhnovskogo-desktop.webp',
        'static_card_mobile': 'images/portfolio/screens/vezhi-rozhnovskogo-mobile.webp',
        'order': 43,
        'home_order': 99,
        'show_on_portfolio': True,
        'show_on_homepage': False,
    },
    {
        'slug': 'ajeres',
        'title': 'AJERES',
        'subtitle': 'FOOD DISTRIBUTOR',
        'title_ru': 'AJERES',
        'subtitle_ru': 'ДИСТРИБУЦИЯ ПРОДУКТОВ',
        'card_description': (
            'Корпоративний сайт (англійська версія) імпортера й дистриб’ютора продуктів харчування '
            'в Узбекистані: ексклюзивні бренди, логістика та вихід виробників на ринок.'
        ),
        'card_description_ru': (
            'Корпоративный сайт (английская версия) импортёра и дистрибьютора продуктов питания в '
            'Узбекистане: эксклюзивные бренды, логистика и выход производителей на рынок.'
        ),
        'integrations': (
            'каталог брендів\n'
            'мультимовність (EN/RU/UZ)\n'
            'форма для партнерів\n'
            'логістичні маршрути'
        ),
        'card_image_alt': 'AJERES — food distributor',
        'card_image_alt_ru': 'AJERES — дистрибуция продуктов',
        'site_url': 'https://ajeres.uz/en/',
        'capture_locale': 'en-US',
        'static_card': 'images/portfolio/screens/ajeres-desktop.webp',
        'static_card_mobile': 'images/portfolio/screens/ajeres-mobile.webp',
        'order': 0,
        'home_order': 99,
        'show_on_portfolio': True,
        'show_on_homepage': False,
    },
    {
        'slug': 'diodi',
        'title': 'ДіОДі',
        'subtitle': 'СТОМАТОЛОГІЯ',
        'title_ru': 'ДиОДи',
        'subtitle_ru': 'СТОМАТОЛОГИЯ',
        'card_description': (
            'Сайт стоматологічної клініки «ДіОДі» в Івано-Франківську: повний спектр послуг, '
            'запис на прийом і портфоліо робіт клініки з понад 24-річним досвідом.'
        ),
        'card_description_ru': (
            'Сайт стоматологической клиники «ДиОДи» в Ивано-Франковске: полный спектр услуг, '
            'запись на приём и портфолио работ клиники с более чем 24-летним опытом.'
        ),
        'integrations': (
            'онлайн-запис на прийом\n'
            'каталог послуг\n'
            'галерея робіт «до/після»\n'
            'відгуки пацієнтів'
        ),
        'card_image_alt': 'ДіОДі — стоматологічна клініка',
        'card_image_alt_ru': 'ДиОДи — стоматологическая клиника',
        'site_url': 'https://diodi.if.ua/',
        'capture_locale': 'uk-UA',
        'static_card': 'images/portfolio/screens/diodi-desktop.webp',
        'static_card_mobile': 'images/portfolio/screens/diodi-mobile.webp',
        'order': 42,
        'home_order': 99,
        'show_on_portfolio': True,
        'show_on_homepage': False,
    },
    {
        'slug': 'favorit-metal',
        'title': 'Фаворит',
        'subtitle': 'ХУДОЖНЄ ЛИТВО МЕТАЛУ',
        'title_ru': 'Фаворит',
        'subtitle_ru': 'ХУДОЖЕСТВЕННОЕ ЛИТЬЁ МЕТАЛЛА',
        'card_description': (
            'Сайт майстерні художнього литва металу та ювелірних виробів на замовлення: музейні '
            'репліки з латуні, бронзи та срібла.'
        ),
        'card_description_ru': (
            'Сайт мастерской художественного литья металла и ювелирных изделий на заказ: музейные '
            'реплики из латуни, бронзы и серебра.'
        ),
        'integrations': (
            'каталог виробів\n'
            'заявка на індивідуальне замовлення\n'
            'галерея робіт\n'
            'портфоліо музейних реплік'
        ),
        'card_image_alt': 'Фаворит — художнє литво металу',
        'card_image_alt_ru': 'Фаворит — художественное литьё металла',
        'site_url': 'https://favorit-metal.com.ua/',
        'capture_locale': 'uk-UA',
        'static_card': 'images/portfolio/screens/favorit-metal-desktop.webp',
        'static_card_mobile': 'images/portfolio/screens/favorit-metal-mobile.webp',
        'order': 20,
        'home_order': 99,
        'show_on_portfolio': True,
        'show_on_homepage': False,
    },
    {
        'slug': 'zubroom',
        'title': 'ЗубRoom',
        'subtitle': 'СТОМАТОЛОГІЯ',
        'title_ru': 'ЗубRoom',
        'subtitle_ru': 'СТОМАТОЛОГИЯ',
        'card_description': (
            'Сайт стоматологічної клініки «ЗубRoom»: сучасні технології лікування, онлайн-запис '
            'та турбота про комфорт пацієнта.'
        ),
        'card_description_ru': (
            'Сайт стоматологической клиники «ЗубRoom»: современные технологии лечения, '
            'онлайн-запись и забота о комфорте пациента.'
        ),
        'integrations': (
            'онлайн-запис на прийом\n'
            'каталог послуг\n'
            'ціни на лікування\n'
            'відгуки пацієнтів'
        ),
        'card_image_alt': 'ЗубRoom — стоматологічна клініка',
        'card_image_alt_ru': 'ЗубRoom — стоматологическая клиника',
        'site_url': 'https://zubroom.com.ua/',
        'capture_locale': 'uk-UA',
        'static_card': 'images/portfolio/screens/zubroom-desktop.webp',
        'static_card_mobile': 'images/portfolio/screens/zubroom-mobile.webp',
        'order': 21,
        'home_order': 99,
        'show_on_portfolio': True,
        'show_on_homepage': False,
    },
]
