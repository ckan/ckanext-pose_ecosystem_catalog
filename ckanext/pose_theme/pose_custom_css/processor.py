from collections import defaultdict, OrderedDict
import wcag_contrast_ratio as contrast
from ckan.plugins.toolkit import ValidationError
from ckanext.pose_theme.base.processor import AbstractParser
from ckanext.pose_theme.base.color_contrast import get_contrast


__all__ = ['custom_style_processor']


class AccountHeaderBackGroundColor(AbstractParser):
    class_name = '.account-masthead'
    form_name = 'account-header-background-color'
    title = 'Account Header Background Color'
    location = 'background'
    _default_value = '#165cab'


class AccountHeaderHoverBackgroundColor(AbstractParser):
    class_name = '.account-masthead .account ul li a:hover'
    form_name = 'account-header-hover-background-color'
    title = 'Account Header Hover Background Color'
    location = 'background'
    _default_value = '#1f76d8'


class AccountHeaderTextColor(AbstractParser):
    class_name = '.account-masthead .account ul li a'
    form_name = 'account-header-text-color'
    title = 'Account Header Text Color'
    location = 'color'
    _default_value = '#ffffff'


class NavigationHeaderBackGroundColor(AbstractParser):
    class_name = '.masthead'
    form_name = 'nav-header-background-color'
    title = 'Navigation Header Background Color'
    location = 'background'
    _default_value = '#ffffff'


class NavigationHeaderHoverBackgroundColor(AbstractParser):
    class_name = ('.masthead .navigation .nav-pills li a:hover,'
                  '.masthead .navigation .nav-pills li.active a,'
                  '.navbar-toggle')
    form_name = 'nav-header-hover-background-color'
    title = 'Navigation Header Hover Background Color'
    location = 'background-color'
    _default_value = '#1f76d8'


class NavigationHeaderTextColor(AbstractParser):
    class_name = ('.navbar .nav>li>a,'
                  '.masthead .nav>li>a,'
                  '.navbar hgroup>h1>a,'
                  '.navbar hgroup>h2')
    form_name = 'nav-header-text-color'
    title = 'Navigation Header Text Color'
    location = 'color'
    _default_value = '#07305c'


class ModuleHeaderBackgroundColor(AbstractParser):
    class_name = '.module-heading'
    form_name = 'module-header-background-color'
    title = 'Side Menu Header Background Color'
    location = 'background'
    _default_value = '#165cab'


class ModuleHeaderTextColor(AbstractParser):
    class_name = ('.module-heading,'
                  '.module-heading .action')
    form_name = 'module-header-text-color'
    title = 'Side Menu Header Text Color'
    location = 'color'
    _default_value = '#ffffff'


class FooterBackGroundColor(AbstractParser):
    class_name = 'body, .site-footer, .footer-column-form .cke_reset'
    form_name = 'footer-background-color'
    title = 'Footer Background Color'
    location = 'background'
    _default_value = '#07305c'


class FooterLinkColor(AbstractParser):
    class_name = ('.site-footer a,'
                  '.site-footer a:hover,'
                  '.footer-column-form .cke_reset a')
    form_name = 'footer-link-text-color'
    title = 'Footer Link Color'
    location = 'color'
    _default_value = '#ffffff'


class FooterTextColor(AbstractParser):
    class_name = ('.site-footer,'
                  '.site-footer label,'
                  '.site-footer small,'
                  '.footer-column-form .cke_reset')
    form_name = 'footer-text-color'
    title = 'Footer Text Color'
    location = 'color'
    _default_value = '#ffffff'


class CustomStyleProcessor:
    def __init__(self):
        self.processor_account_header_background_color = AccountHeaderBackGroundColor()
        self.processor_account_header_text_color = AccountHeaderTextColor()
        self.processor_account_header_hover_background_color = AccountHeaderHoverBackgroundColor()

        self.processor_navigation_header_background_color = NavigationHeaderBackGroundColor()
        self.processor_navigation_header_text_color = NavigationHeaderTextColor()
        self.processor_navigation_header_hover_background_color = NavigationHeaderHoverBackgroundColor()

        self.processor_module_header_background_color = ModuleHeaderBackgroundColor()
        self.processor_module_header_text_color = ModuleHeaderTextColor()

        self.processor_footer_background_color = FooterBackGroundColor()
        self.processor_footer_text_color = FooterTextColor()
        self.processor_footer_link_color = FooterLinkColor()

        self.processors = (
            self.processor_account_header_background_color,
            self.processor_account_header_hover_background_color,
            self.processor_account_header_text_color,

            self.processor_navigation_header_background_color,
            self.processor_navigation_header_hover_background_color,
            self.processor_navigation_header_text_color,

            self.processor_module_header_background_color,
            self.processor_module_header_text_color,

            self.processor_footer_background_color,
            self.processor_footer_link_color,
            self.processor_footer_text_color
        )

    def get_custom_css(self, data):
        result_css = defaultdict(dict)
        css_metadata = OrderedDict()

        for processor in self.processors:
            css_declaration = processor.get_css_from_data(data)
            if css_declaration is not None:
                result_css[processor.class_name].update(css_declaration)

            css_metadata[processor.form_name] = {
                'title': processor.title,
                'value': processor.value,
            }

        raw_css = '\n'
        for class_name, css_declaration in result_css.items():
            css_declaration = str(css_declaration).replace(',', ';').replace("'", "")
            raw_css = '{previous_block}\n {css_selector} {css_declaration}'.format(
                previous_block=raw_css,
                css_selector=class_name,
                css_declaration=css_declaration)

        return raw_css, css_metadata

    def check_contrast(self):
        errors = {}
        color_pairs = [
            (self.processor_account_header_background_color, self.processor_account_header_text_color),
            (self.processor_navigation_header_background_color, self.processor_navigation_header_text_color),
            (self.processor_module_header_background_color, self.processor_module_header_text_color),
            (self.processor_footer_background_color, self.processor_footer_text_color),
            (self.processor_footer_background_color, self.processor_footer_link_color)
        ]
        for pair in color_pairs:
            pr_1 = pair[0]
            pr_2 = pair[1]
            if pr_1.value and pr_2.value:
                contrast_value = get_contrast(pr_1.value, pr_2.value)
                if not contrast.passes_AA(contrast_value, large=True):
                    key = '{} and {}'.format(pr_1.title, pr_2.title)
                    errors[key] = 'Contrast ratio is not high enough.'
        if errors:
            raise ValidationError(errors)


custom_style_processor = CustomStyleProcessor()
