from django.db import models
from django.urls import reverse
from django.utils.html import strip_tags
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

# Категорії, сховані на публічному сайті prometeylabs.cz (аудит 19.10.2026, №70).
# Статті НЕ видаляються і лишаються в адмінці; прибираються лише з публічних
# списків, пошуку, «схожих», sitemap, а detail віддає 404.
HIDDEN_PUBLIC_CATEGORIES = ('courses',)


class BlogPostQuerySet(models.QuerySet):
    def public(self):
        """Опубліковані статті без схованих на .cz категорій."""
        return self.filter(is_published=True).exclude(category__in=HIDDEN_PUBLIC_CATEGORIES)


class BlogPost(models.Model):
    title = models.CharField(max_length=200, verbose_name=_("Заголовок"))
    slug = models.SlugField(max_length=200, unique=True, verbose_name=_("URL"))
    excerpt = models.TextField(max_length=300, verbose_name=_("Короткий опис"))
    content = models.TextField(verbose_name=_("Контент"))
    title_ru = models.CharField(max_length=200, blank=True, verbose_name=_("Заголовок (RU)"))
    title_en = models.CharField(max_length=200, blank=True, verbose_name=_("Заголовок (EN)"))
    title_cs = models.CharField(max_length=200, blank=True, verbose_name=_("Заголовок (CS)"))
    excerpt_ru = models.TextField(max_length=300, blank=True, verbose_name=_("Короткий опис (RU)"))
    excerpt_en = models.TextField(max_length=300, blank=True, verbose_name=_("Короткий опис (EN)"))
    excerpt_cs = models.TextField(max_length=300, blank=True, verbose_name=_("Короткий опис (CS)"))
    content_ru = models.TextField(blank=True, verbose_name=_("Контент (RU)"))
    content_en = models.TextField(blank=True, verbose_name=_("Контент (EN)"))
    content_cs = models.TextField(blank=True, verbose_name=_("Контент (CS)"))
    seo_title = models.CharField(max_length=70, verbose_name=_("SEO заголовок"))
    seo_description = models.CharField(max_length=160, verbose_name=_("SEO опис"))
    keywords = models.CharField(max_length=255, verbose_name=_("Ключові слова"))
    keywords_ru = models.CharField(max_length=255, blank=True, verbose_name=_("Ключові слова (RU)"))
    keywords_en = models.CharField(max_length=255, blank=True, verbose_name=_("Ключові слова (EN)"))
    keywords_cs = models.CharField(max_length=255, blank=True, verbose_name=_("Ключові слова (CS)"))
    
    # Нові поля для SEO
    meta_title = models.CharField(max_length=60, verbose_name=_("Meta Title"), blank=True)
    meta_description = models.CharField(max_length=160, verbose_name=_("Meta Description"), blank=True)
    og_title = models.CharField(max_length=60, verbose_name=_("OG Title"), blank=True)
    og_description = models.CharField(max_length=160, verbose_name=_("OG Description"), blank=True)
    
    # Додаткові поля
    reading_time = models.PositiveIntegerField(default=5, verbose_name=_("Час читання (хв)"))
    featured_image = models.ImageField(upload_to='blog/', verbose_name=_("Головне зображення"), blank=True)
    category = models.CharField(max_length=50, choices=[
        ('web-development', _('Веб-розробка')),
        ('courses', _('Курси програмування')),
        ('telegram-bots', _('Telegram боти')),
        ('business', _('Бізнес')),
        ('technology', _('Технології')),
        ('ai-development', _('AI розробка')),
        ('ai-agents', _('AI агенти')),
        ('ai-automation', _('AI автоматизація')),
    ], default='web-development', verbose_name=_("Категорія"))
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Створено"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Оновлено"))
    is_published = models.BooleanField(default=True, verbose_name=_("Опубліковано"))

    objects = BlogPostQuerySet.as_manager()
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _("Стаття блогу")
        verbose_name_plural = _("Статті блогу")
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        plain_title = strip_tags(self.title or '')
        plain_excerpt = strip_tags(self.excerpt or '')

        if not self.slug:
            self.slug = slugify(plain_title)

        if not self.meta_title:
            self.meta_title = plain_title[:60]
        if not self.meta_description:
            self.meta_description = plain_excerpt[:160]
        if not self.og_title:
            self.og_title = plain_title[:60]
        if not self.og_description:
            self.og_description = plain_excerpt[:160]
            
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('blog:blog_detail', kwargs={'slug': self.slug})
    
    def get_keywords_list(self):
        """Повертає список ключових слів"""
        keywords = self.get_localized_keywords()
        if keywords:
            return [keyword.strip() for keyword in keywords.split(',')]
        return []

    def get_localized_title(self) -> str:
        from apps.core.i18n_content import localized_text

        return localized_text(self.title, self.title_ru, self.title_en, self.title_cs)

    def get_localized_excerpt(self) -> str:
        from apps.core.i18n_content import localized_text

        return localized_text(self.excerpt, self.excerpt_ru, self.excerpt_en, self.excerpt_cs)

    def get_localized_content(self) -> str:
        from apps.core.i18n_content import localized_text

        return localized_text(self.content, self.content_ru, self.content_en, self.content_cs)

    def get_localized_keywords(self) -> str:
        from apps.core.i18n_content import localized_text

        return localized_text(self.keywords, self.keywords_ru, self.keywords_en, self.keywords_cs)
    
    def get_reading_time_text(self):
        """Повертає текст часу читання"""
        if self.reading_time == 1:
            return "1 хвилина"
        elif self.reading_time < 5:
            return f"{self.reading_time} хвилини"
        else:
            return f"{self.reading_time} хвилин"
    
    def get_clean_content(self):
        """Повертає контент без зірочок та форматований для журнального стилю"""
        import re
        content = self.get_localized_content()
        
        # Прибираємо подвійні зірочки (жирний текст в markdown)
        content = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', content)
        
        # Прибираємо одинарні зірочки
        content = content.replace('*', '')
        
        # Конвертуємо markdown заголовки в HTML
        content = re.sub(r'^### (.+)$', r'<h3>\1</h3>', content, flags=re.MULTILINE)
        content = re.sub(r'^## (.+)$', r'<h2>\1</h2>', content, flags=re.MULTILINE)
        content = re.sub(r'^# (.+)$', r'<h1>\1</h1>', content, flags=re.MULTILINE)
        
        # Конвертуємо параграфи
        lines = content.split('\n')
        formatted_lines = []
        in_paragraph = False
        in_blockquote = False
        in_list = False
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                if in_paragraph:
                    formatted_lines.append('</p>')
                    in_paragraph = False
                if in_blockquote:
                    formatted_lines.append('</blockquote>')
                    in_blockquote = False
                if in_list:
                    formatted_lines.append('</ul>')
                    in_list = False
                formatted_lines.append('')
            elif line.startswith('<h') or line.startswith('</h'):
                if in_paragraph:
                    formatted_lines.append('</p>')
                    in_paragraph = False
                if in_blockquote:
                    formatted_lines.append('</blockquote>')
                    in_blockquote = False
                if in_list:
                    formatted_lines.append('</ul>')
                    in_list = False
                formatted_lines.append(line)
            elif line.startswith('>'):
                # Цитата (blockquote)
                if in_paragraph:
                    formatted_lines.append('</p>')
                    in_paragraph = False
                if in_list:
                    formatted_lines.append('</ul>')
                    in_list = False
                if not in_blockquote:
                    formatted_lines.append('<blockquote>')
                    in_blockquote = True
                quote_text = line[1:].strip()
                if quote_text:
                    formatted_lines.append(f'<p>{quote_text}</p>')
            elif line.startswith('-'):
                if in_paragraph:
                    formatted_lines.append('</p>')
                    in_paragraph = False
                if in_blockquote:
                    formatted_lines.append('</blockquote>')
                    in_blockquote = False
                if not in_list:
                    formatted_lines.append('<ul>')
                    in_list = True
                formatted_lines.append(f'<li>{line[1:].strip()}</li>')
            else:
                if in_blockquote:
                    formatted_lines.append('</blockquote>')
                    in_blockquote = False
                if in_list:
                    formatted_lines.append('</ul>')
                    in_list = False
                if not in_paragraph and not line.startswith('<'):
                    formatted_lines.append('<p>')
                    in_paragraph = True
                formatted_lines.append(line)
        
        if in_paragraph:
            formatted_lines.append('</p>')
        if in_blockquote:
            formatted_lines.append('</blockquote>')
        if in_list:
            formatted_lines.append('</ul>')
        
        content = '\n'.join(formatted_lines)

        return content

    def get_safe_content(self):
        """HTML з TinyMCE (bleach) або legacy markdown."""
        from .html_sanitize import content_looks_like_html, sanitize_blog_html

        raw = self.get_localized_content() or ''
        if content_looks_like_html(raw):
            return sanitize_blog_html(raw)
        return self.get_clean_content()

    def get_safe_title(self):
        from .html_sanitize import content_looks_like_html, sanitize_blog_title

        raw = self.get_localized_title() or ''
        if content_looks_like_html(raw):
            return sanitize_blog_title(raw)
        return raw

    def get_safe_excerpt(self):
        from .html_sanitize import content_looks_like_html, sanitize_blog_html

        raw = self.get_localized_excerpt() or ''
        if content_looks_like_html(raw):
            return sanitize_blog_html(raw)
        return raw
