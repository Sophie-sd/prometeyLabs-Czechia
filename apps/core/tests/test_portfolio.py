from django.test import SimpleTestCase, override_settings

from apps.core.models import PortfolioProject
from apps.core.portfolio_images import resolve_portfolio_image_url
from apps.core.portfolio_sanitize import linkify_portfolio_html, sanitize_portfolio_html


class PortfolioSanitizeTests(SimpleTestCase):
    def test_strips_script(self):
        dirty = '<p>Hello</p><script>alert(1)</script>'
        clean = sanitize_portfolio_html(dirty)
        self.assertIn('<p>Hello</p>', clean)
        self.assertNotIn('script', clean.lower())

    def test_keeps_safe_img(self):
        html = '<img src="/media/portfolio/test.png" alt="Test" class="portfolio-modal-image-full">'
        clean = linkify_portfolio_html(html)
        self.assertIn('/media/portfolio/test.png', clean)

    def test_blocks_unsafe_img_src(self):
        html = '<img src="javascript:alert(1)" alt="X">'
        clean = linkify_portfolio_html(html)
        self.assertNotIn('javascript:', clean)


class PortfolioImageFallbackTests(SimpleTestCase):
    @override_settings(MEDIA_ROOT='/tmp/prometey-empty-media-test')
    def test_static_fallback_when_media_missing(self):
        project = PortfolioProject(
            title='ZNOMax',
            slug='znomax',
            card_description='Desc',
        )
        project.card_image.name = 'portfolio/znomax/znomax.webp'
        src = resolve_portfolio_image_url(project, 'card_image')
        self.assertIn('images/portfolio/screens/znomax-desktop.webp', src)

    def test_home_image_falls_back_to_card_static(self):
        """home_story_image не заповнюється для нового портфоліо — get_home_image_src
        падає на static card_image (znomax) замість media-файлу, якого нема."""
        project = PortfolioProject(
            title='ZNOMax',
            slug='znomax',
            card_description='Desc',
        )
        project.home_story_image.name = 'portfolio/znomax/home_missing.png'
        src = project.get_home_image_src()
        self.assertIn('images/portfolio/screens/znomax-desktop.webp', src)
        self.assertNotIn('/media/', src)


class PortfolioModelTests(SimpleTestCase):
    def test_integration_tags_parsing(self):
        project = PortfolioProject(
            title='Test',
            slug='test',
            card_description='Desc',
            integrations='tag one\ntag two\n\n',
        )
        self.assertEqual(project.get_integration_tags(), ['tag one', 'tag two'])

    def test_layout_modifier_even_index_no_flip(self):
        project = PortfolioProject(title='T', slug='t', card_description='D', order=99)
        self.assertEqual(project.get_layout_modifier(0), '')
        self.assertEqual(project.get_layout_modifier(2), '')

    def test_layout_modifier_odd_index_flip(self):
        project = PortfolioProject(title='T', slug='t', card_description='D', order=0)
        self.assertEqual(project.get_layout_modifier(1), 'pf-snap--flip')
        self.assertEqual(project.get_layout_modifier(3), 'pf-snap--flip')

    def test_snap_tone_cycle(self):
        self.assertEqual(PortfolioProject.get_snap_tone(0), 'orange')
        self.assertEqual(PortfolioProject.get_snap_tone(1), 'gray')
        self.assertEqual(PortfolioProject.get_snap_tone(2), 'purple')
        self.assertEqual(PortfolioProject.get_snap_tone(3), 'orange')
        self.assertEqual(PortfolioProject.get_snap_tone(4), 'gray')
        self.assertEqual(PortfolioProject.get_snap_tone(5), 'purple')

    def test_safe_cta_href_blocks_javascript(self):
        project = PortfolioProject(
            title='T',
            slug='t',
            card_description='D',
            cta_url='javascript:alert(1)',
        )
        self.assertEqual(project.get_safe_cta_href(), '')

    def test_safe_cta_href_allows_internal_and_https(self):
        internal = PortfolioProject(
            title='T',
            slug='t',
            card_description='D',
            cta_url='/contacts/',
        )
        external = PortfolioProject(
            title='T2',
            slug='t2',
            card_description='D',
            cta_url='https://example.com/case',
        )
        self.assertEqual(internal.get_safe_cta_href(), '/contacts/')
        self.assertEqual(external.get_safe_cta_href(), 'https://example.com/case')
        self.assertFalse(internal.is_external_cta())
        self.assertTrue(external.is_external_cta())

    def test_localized_title_and_tags_follow_language(self):
        from django.utils import translation

        project = PortfolioProject(
            title='Střechy',
            title_en='Roofing',
            title_cs='Střechy',
            title_ru='',
            slug='pokrivlya',
            card_description='CS desc',
            card_description_en='EN desc',
            card_description_cs='CS desc',
            integrations='střechy\npoptávka',
            integrations_en='roofing\nenquiry',
            integrations_cs='střechy\npoptávka',
            integrations_ru='',
        )
        translation.activate('en')
        self.assertEqual(project.get_localized_title(), 'Roofing')
        self.assertEqual(project.get_localized_card_description(), 'EN desc')
        self.assertEqual(project.get_integration_tags(), ['roofing', 'enquiry'])
        translation.activate('cs')
        self.assertEqual(project.get_localized_title(), 'Střechy')
        self.assertEqual(project.get_integration_tags(), ['střechy', 'poptávka'])
        translation.deactivate()

    def test_watermark_mark(self):
        project = PortfolioProject(title='Speak Up', slug='speakup', card_description='D')
        self.assertEqual(project.get_watermark_mark(), 'S')

    def test_modal_id(self):
        project = PortfolioProject(title='T', slug='speakup', card_description='D')
        self.assertEqual(project.get_modal_id(), 'project-speakup-modal')

