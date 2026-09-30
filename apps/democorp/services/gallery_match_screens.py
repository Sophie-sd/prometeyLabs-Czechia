"""Скріни галереї «Як працюємо»: UI на студійному тлі, срібло рамки, яскраве золото."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

from .example_screens import _font, _text

BG = (22, 16, 14)
BAR = (36, 26, 20)
GOLD = (236, 190, 82)
CHAMPAGNE = (246, 228, 176)
CREAM = (255, 248, 236)
MUTED = (214, 196, 172)
SLOT = (58, 44, 34)
SILVER = (198, 178, 156)
SILVER_DARK = (142, 124, 108)
STUDIO = (42, 28, 20)
STUDIO_GLOW = (78, 52, 34)

W, H = 1200, 900
SEED_DIR = Path(__file__).resolve().parents[3] / 'static' / 'democorp' / 'seed' / 'gallery'
PHONE = (420, 48, 780, 852)
PHONE_SCREENS = frozenset({'phone.webp', 'menu.webp'})


def _studio() -> Image.Image:
    base = Image.new('RGB', (W, H), STUDIO)
    glow = Image.new('RGB', (W, H), STUDIO_GLOW)
    mask = Image.new('L', (W, H), 0)
    ImageDraw.Draw(mask).ellipse((W // 2 - 520, H // 2 - 380, W // 2 + 520, H // 2 + 420), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(90))
    return Image.composite(glow, base, mask)


def _as_laptop(ui: Image.Image) -> Image.Image:
    canvas = _studio()
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle((72, 36, 1128, 700), radius=20, fill=SILVER)
    draw.rounded_rectangle((76, 40, 1124, 696), radius=18, fill=SILVER_DARK)
    inner = (90, 54, 1110, 674)
    draw.rounded_rectangle(inner, radius=6, fill=BG)
    screen = ui.resize((inner[2] - inner[0], inner[3] - inner[1]), Image.Resampling.LANCZOS)
    canvas.paste(screen, (inner[0], inner[1]))
    draw.rounded_rectangle((48, 698, 1152, 748), radius=8, fill=SILVER)
    draw.rectangle((80, 710, 1120, 722), fill=SILVER_DARK)
    cx = W // 2
    draw.ellipse((cx - 5, 42, cx + 5, 52), fill=(40, 30, 24))
    return canvas


def _header(draw: ImageDraw.ImageDraw, nav: tuple[str, ...]) -> None:
    draw.rectangle((0, 0, W, 72), fill=BAR)
    draw.line((0, 72, W, 72), fill=GOLD, width=2)
    _text(draw, (40, 28), 'PROMETEYLABS', _font(16, bold=True), CHAMPAGNE)
    item_f = _font(13)
    x = W - 40
    for label in reversed(nav):
        bbox = draw.textbbox((0, 0), label, font=item_f)
        tw = bbox[2] - bbox[0]
        x -= tw
        _text(draw, (x, 30), label, item_f, MUTED)
        x -= 28


def _cta(draw: ImageDraw.ImageDraw, xy: tuple[int, int], label: str) -> None:
    font = _font(14, bold=True)
    bbox = draw.textbbox((0, 0), label, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x0, y0 = xy
    draw.rectangle((x0, y0, x0 + tw + 44, y0 + th + 28), fill=CHAMPAGNE)
    _text(draw, (x0 + 22, y0 + 12), label, font, BG)


def _field(draw: ImageDraw.ImageDraw, xy: tuple[int, int], w: int, h: int, label: str, value: str) -> None:
    x, y = xy
    _text(draw, (x, y), label.upper(), _font(12, bold=True), GOLD)
    draw.rectangle((x, y + 24, x + w, y + 24 + h), fill=SLOT)
    draw.rectangle((x, y + 24, x + w, y + 24 + h), outline=GOLD, width=2)
    _text(draw, (x + 16, y + 36), value, _font(15), CREAM)


def _phone_shell(draw: ImageDraw.ImageDraw) -> tuple[int, int, int, int]:
    x0, y0, x1, y1 = PHONE
    draw.rounded_rectangle((x0, y0, x1, y1), radius=42, fill=SILVER)
    draw.rounded_rectangle((x0 + 5, y0 + 5, x1 - 5, y1 - 5), radius=38, fill=SILVER_DARK)
    sx0, sy0, sx1, sy1 = x0 + 16, y0 + 16, x1 - 16, y1 - 16
    draw.rounded_rectangle((sx0, sy0, sx1, sy1), radius=28, fill=BG)
    draw.rounded_rectangle((470, 62, 730, 86), radius=12, fill=BAR)
    return sx0, sy0, sx1, sy1


def _paint_admin(image: Image.Image) -> None:
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 280, H), fill=BAR)
    draw.line((280, 0, 280, H), fill=GOLD, width=2)
    _text(draw, (28, 36), 'PROMETEYLABS', _font(16, bold=True), CHAMPAGNE)
    _text(draw, (28, 64), 'Адмінка', _font(13), MUTED)
    nav = _font(15)
    for y, label, active in ((120, 'Тексти', True), (168, 'Фото', False), (216, 'Заявки', False)):
        if active:
            draw.rectangle((16, y - 10, 264, y + 28), outline=GOLD, width=2)
            _text(draw, (32, y), label, nav, CREAM)
        else:
            _text(draw, (32, y), label, nav, MUTED)
    _text(draw, (332, 40), 'Головна сторінка', _font(28, bold=True), CREAM)
    _text(draw, (332, 84), 'Тексти правите самі — без програміста.', _font(16), MUTED)
    _field(draw, (332, 150), 812, 56, 'Заголовок', 'Кілька сторінок — і люди пишуть вам')
    _field(
        draw, (332, 258), 812, 132, 'Підзаголовок',
        'Головна, послуги, про нас, контакти.\nЗрозумілі слова, зручно з телефону.',
    )
    _cta(draw, (332, 440), 'ЗБЕРЕГТИ ЗМІНИ')


def _paint_phone(image: Image.Image) -> None:
    draw = ImageDraw.Draw(image)
    _phone_shell(draw)
    _text(draw, (500, 108), 'PROMETEYLABS', _font(13, bold=True), CHAMPAGNE)
    _text(draw, (456, 160), 'Кілька сторінок —\nі люди пишуть вам', _font(22, bold=True), CREAM)
    _text(draw, (456, 250), 'Зручно з телефону.\nБез щипка й зуму.', _font(14), MUTED)
    _cta(draw, (456, 340), 'ЗАЯВКА')
    y = 430
    for num, label in (('0.8s', 'завантаження'), ('44px', 'кнопки'), ('100%', 'з телефону')):
        draw.line((456, y, 744, y), fill=SLOT, width=1)
        _text(draw, (456, y + 16), num, _font(20, bold=True), GOLD)
        _text(draw, (560, y + 20), label, _font(13), MUTED)
        y += 64


def _paint_tilt_cards(image: Image.Image) -> None:
    draw = ImageDraw.Draw(image)
    _header(draw, ('Головна', 'Послуги', 'Контакти'))
    _text(draw, (40, 110), 'Картки послуг', _font(32, bold=True), CREAM)
    _text(draw, (40, 158), 'Нахиляються при наведенні — видно обʼєм.', _font(16), MUTED)
    cards = (
        ('01', 'Стратегія', 'Структура сторінок\nдо збірки'),
        ('02', 'Збірка', 'Форма, телефон,\nзаявки вам'),
        ('03', 'Адмінка', 'Тексти правите\nсамі'),
    )
    gap, left, top, height = 24, 40, 230, 520
    width = (W - 40 * 2 - gap * 2) // 3
    for i, (num, title, body) in enumerate(cards):
        x = left + i * (width + gap)
        y = top - (18 if i == 1 else 0)
        draw.rectangle((x, y, x + width, y + height), fill=SLOT)
        draw.rectangle((x, y, x + width, y + height), outline=GOLD, width=2)
        _text(draw, (x + 24, y + 28), num, _font(18, bold=True), GOLD)
        _text(draw, (x + 24, y + 72), title.upper(), _font(20, bold=True), CREAM)
        _text(draw, (x + 24, y + 130), body, _font(15), MUTED)
        draw.rectangle((x + 24, y + height - 88, x + width - 24, y + height - 32), outline=GOLD, width=1)


def _paint_menu(image: Image.Image) -> None:
    draw = ImageDraw.Draw(image)
    _phone_shell(draw)
    _text(draw, (500, 108), 'PROMETEYLABS', _font(13, bold=True), CHAMPAGNE)
    _text(draw, (708, 108), 'x', _font(16), MUTED)
    _text(draw, (456, 168), 'Меню', _font(22, bold=True), CREAM)
    items = (
        ('Головна', True),
        ('Як працюємо', False),
        ('Приклади', False),
        ('Про нас', False),
        ('Контакти', False),
    )
    y = 230
    for label, current in items:
        color = CREAM if current else MUTED
        _text(draw, (456, y), label, _font(18), color)
        if current:
            draw.line((456, y + 32, 540, y + 32), fill=GOLD, width=2)
        y += 56
    _cta(draw, (456, 540), 'ЗАЯВКА')


def _paint_stats(image: Image.Image) -> None:
    draw = ImageDraw.Draw(image)
    _header(draw, ('Головна', 'Цифри', 'Контакти'))
    _text(draw, (40, 120), 'Цифри, що рахуються', _font(32, bold=True), CREAM)
    _text(draw, (40, 172), 'На екрані зʼявляються самі — видно результат.', _font(16), MUTED)
    stats = (
        ('7', 'днів до старту'),
        ('4', 'сторінки в комплекті'),
        ('24', 'години відповіді'),
        ('100%', 'зручно з телефону'),
    )
    gap, left, top, height = 20, 40, 260, 420
    width = (W - 40 * 2 - gap * 3) // 4
    for i, (num, label) in enumerate(stats):
        x = left + i * (width + gap)
        draw.rectangle((x, top, x + width, top + height), fill=SLOT)
        draw.rectangle((x, top, x + width, top + height), outline=GOLD, width=2)
        _text(draw, (x + 24, top + 80), num, _font(48, bold=True), GOLD)
        draw.line((x + 24, top + 160, x + width - 24, top + 160), fill=GOLD, width=2)
        _text(draw, (x + 24, top + 190), label, _font(16), CREAM)


def _paint_form(image: Image.Image) -> None:
    draw = ImageDraw.Draw(image)
    _header(draw, ('Головна', 'Контакти'))
    _text(draw, (40, 110), 'Залиште заявку', _font(32, bold=True), CREAM)
    _text(draw, (40, 158), 'Після форми вам пишуть — заявка приходить вам.', _font(16), MUTED)
    _field(draw, (40, 230), 1120, 52, 'Імʼя', 'Олена')
    _field(draw, (40, 330), 540, 52, 'Telefon', '+420 777 000 000')
    _field(draw, (620, 330), 540, 52, 'Email', 'you@company.com')
    _field(draw, (40, 430), 1120, 140, 'Повідомлення', 'Потрібен сайт на кілька сторінок.')
    _cta(draw, (40, 640), 'ЗАЛИШИТИ ЗАЯВКУ')


SCREENS = (
    ('admin.webp', _paint_admin),
    ('phone.webp', _paint_phone),
    ('tilt-cards.webp', _paint_tilt_cards),
    ('menu.webp', _paint_menu),
    ('stats.webp', _paint_stats),
    ('form.webp', _paint_form),
)


def write_screens(out_dir: Path | None = None) -> list[Path]:
    target = out_dir or SEED_DIR
    target.mkdir(parents=True, exist_ok=True)
    written = []
    for name, painter in SCREENS:
        if name in PHONE_SCREENS:
            image = _studio()
            painter(image)
        else:
            ui = Image.new('RGB', (W, H), BG)
            painter(ui)
            image = _as_laptop(ui)
        path = target / name
        image.save(path, format='WEBP', quality=86, method=6)
        written.append(path)
    return written
