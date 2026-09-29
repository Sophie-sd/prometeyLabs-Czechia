"""«Мій магазин» — єдина CMS-сторінка: тексти, фото, кольори, hero-слайди.

ShopBlock/ShopHeroSlide НЕ мають окремого CRUD ModelAdmin (admin_cms_blocks_skill
§14) — уся робота йде через `changelist_view` цього проксі, обмежену власним shop.
"""
from django import forms
from django.contrib import admin, messages
from django.forms import modelformset_factory
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin as UnfoldModelAdmin

from .block_defaults import BLOCK_REGISTRY, PAGE_LABELS
from .content_models import ShopBlock, ShopHeroSlide
from .models import DEFAULT_THEME_COLORS, DemoShop

HEX_WIDGET = forms.TextInput(attrs={'type': 'color'})

HeroSlideFormSet = modelformset_factory(
    ShopHeroSlide,
    fields=(
        'image', 'image_narrow', 'title', 'title_cs', 'title_en',
        'subtitle', 'subtitle_cs', 'subtitle_en',
        'cta_label', 'cta_label_cs', 'cta_label_en',
        'is_active', 'order'
    ),
    extra=1,
    can_delete=True,
)


class ShopThemeForm(forms.ModelForm):
    """Кольори теми магазину.

    `<input type=color>` ніколи не буває порожнім (HTML5), тож для порожніх
    полів (= «використовується дефолт із demoshop_tokens.css») підставляємо
    initial = сам дефолт — інакше збереження форми без дотику до свотчів
    записало б #000000 у всі кольори й зламало б вітрину.
    """

    class Meta:
        model = DemoShop
        fields = ('color_primary', 'color_primary_hover', 'color_accent', 'color_surface', 'color_text')
        widgets = {name: HEX_WIDGET for name in fields}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            for name in self.Meta.fields:
                if not getattr(self.instance, name):
                    self.initial[name] = DEFAULT_THEME_COLORS[name]


def _build_block_form(shop):
    """Динамічна форма з полем на кожен запис BLOCK_REGISTRY (CS+EN only)."""
    fields = {}
    for entry in BLOCK_REGISTRY:
        name_base = f"{entry['page']}__{entry['key']}"
        name_en = f"{entry['page']}__{entry['key']}__en"
        name_cs = f"{entry['page']}__{entry['key']}__cs"

        if entry['type'] == 'image':
            fields[name_base] = forms.ImageField(required=False, label=str(entry['label']))
        else:
            widget = forms.Textarea(attrs={'rows': 3}) if entry.get('multiline') else forms.TextInput
            fields[name_cs] = forms.CharField(required=False, label=f"{entry['label']} (CS)", widget=widget)
            fields[name_en] = forms.CharField(required=False, label=f"{entry['label']} (EN)", widget=widget)

    form_class = type('ShopBlockForm', (forms.Form,), fields)

    blocks = {f'{b.page}__{b.key}': b for b in shop.blocks.all()}
    initial = {}
    for entry in BLOCK_REGISTRY:
        name_base = f"{entry['page']}__{entry['key']}"
        block = blocks.get(name_base)
        if entry['type'] != 'image' and block:
            initial[f"{name_base}__cs"] = block.value_text_cs or block.value_text
            initial[f"{name_base}__en"] = block.value_text_en
    return form_class(initial=initial), blocks


def _group_blocks_for_template(form, blocks):
    groups = {}
    for entry in BLOCK_REGISTRY:
        name_base = f"{entry['page']}__{entry['key']}"
        page_group = groups.setdefault(
            entry['page'], {'label': PAGE_LABELS.get(entry['page'], entry['page']), 'fields': []},
        )
        if entry['type'] == 'image':
            page_group['fields'].append({
                'field': form[name_base],
                'type': entry['type'],
                'current_image': blocks.get(name_base).value_image if blocks.get(name_base) else None,
            })
        else:
            page_group['fields'].append({'field': form[f"{name_base}__cs"], 'type': entry['type']})
            page_group['fields'].append({'field': form[f"{name_base}__en"], 'type': entry['type']})
    return list(groups.values())


def _owned_shop_or_none(request):
    if request.user.is_superuser:
        shop_id = request.GET.get('shop')
        return DemoShop.objects.filter(pk=shop_id).first() if shop_id else None
    return getattr(request.user, 'demo_shop', None)


@admin.register(ShopBlock)
class ShopContentAdmin(UnfoldModelAdmin):
    """Реєстрація потрібна лише для стабільного admin URL — звичайний CRUD вимкнено."""

    def has_module_permission(self, request):
        return request.user.is_superuser or getattr(request.user, 'demo_shop', None) is not None

    def has_view_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_change_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        shop = _owned_shop_or_none(request)
        if shop is None:
            messages.error(request, _('До вашого акаунту не привʼязано жодного демо-магазину.'))
            return redirect('admin:index')

        block_form, blocks = _build_block_form(shop)
        theme_form = ShopThemeForm(instance=shop)
        slide_qs = shop.hero_slides.all()
        slide_formset = HeroSlideFormSet(queryset=slide_qs, prefix='slides')

        if request.method == 'POST':
            block_form = type(block_form)(request.POST, request.FILES)
            theme_form = ShopThemeForm(request.POST, instance=shop)
            slide_formset = HeroSlideFormSet(request.POST, request.FILES, queryset=slide_qs, prefix='slides')

            if block_form.is_valid() and theme_form.is_valid() and slide_formset.is_valid():
                for entry in BLOCK_REGISTRY:
                    name = f"{entry['page']}__{entry['key']}"
                    block, _created = ShopBlock.objects.get_or_create(
                        shop=shop, page=entry['page'], key=entry['key'],
                        defaults={'block_type': entry['type'], 'label': str(entry['label'])},
                    )
                    if entry['type'] == 'image':
                        uploaded = block_form.cleaned_data.get(name)
                        if uploaded:
                            block.value_image = uploaded
                            block.save(update_fields=['value_image'])
                    else:
                        cs = block_form.cleaned_data.get(f"{name}__cs", '')
                        en = block_form.cleaned_data.get(f"{name}__en", '')
                        block.value_text_cs = cs
                        block.value_text_en = en
                        block.value_text = cs
                        block.save(update_fields=['value_text', 'value_text_en', 'value_text_cs'])

                theme_form.save()

                for form in slide_formset:
                    if form in slide_formset.deleted_forms:
                        continue
                    # Незмінений «зайвий» рядок (extra=1) без pk теж матиме
                    # has_changed()=False — не створюємо порожній слайд без фото.
                    if not form.has_changed():
                        continue
                    slide = form.save(commit=False)
                    slide.shop = shop
                    slide.save()
                for form in slide_formset.deleted_forms:
                    if form.instance.pk:
                        form.instance.delete()

                messages.success(request, _('Магазин оновлено.'))
                return redirect(request.path)

        context = {
            **self.admin_site.each_context(request),
            'title': _('Мій магазин — контент і кольори'),
            'shop': shop,
            'block_form': block_form,
            'theme_form': theme_form,
            'slide_formset': slide_formset,
            'block_groups': _group_blocks_for_template(block_form, blocks),
        }
        return render(request, 'demoshop/admin/my_shop_content.html', context)
