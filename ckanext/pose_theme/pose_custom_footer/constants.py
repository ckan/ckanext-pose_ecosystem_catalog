CONFIG_KEY = 'ckanext.pose_theme.custom_footer.data'

ALLOWED_TAGS_SET = {
    'a', 'abbr', 'acronym', 'b', 'br', 'div', 'em', 'i',
    'img', 'li', 'ol', 'p', 'path', 'strong', 'svg', 'ul'
}

ALLOWED_TAGS_LIST = [
    'a', 'abbr', 'acronym', 'b', 'br', 'div', 'em', 'i',
    'img', 'li', 'ol', 'p', 'path', 'strong', 'svg', 'ul'
]

ALLOWED_ATTRIBUTES = {
    '*': ['class'],
    'a': ['href', 'class', 'target', 'title', 'aria-label'],
    'img': ['src', 'alt', 'class', 'height', 'style', 'width'],
    'path': ['fill', 'd'],
    'svg': ['aria-hidden', 'focusable', 'role', 'xmlns', 'viewBox']
}

ALLOWED_CSS_PROPERTIES = [
    'background-color', 'border-bottom-color', 'border-collapse',
    'border-color', 'border-left-color', 'border-right-color', 'border-top-color',
    'clear', 'color', 'cursor', 'direction', 'display', 'float', 'font',
    'font-family', 'font-size', 'font-style', 'font-variant', 'font-weight',
    'height', 'letter-spacing', 'line-height', 'max-height', 'max-width',
    'overflow', 'text-align', 'text-decoration', 'text-indent',
    'vertical-align', 'white-space', 'width'
]
