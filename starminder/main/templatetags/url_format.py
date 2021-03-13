from django import template
from django.utils.safestring import mark_safe


register = template.Library()


@register.simple_tag
def url_format(link_format, url, text, title):
    if link_format == "markdown":
        link = f"[{text}]({url} '{title}')"

    if link_format == "html":
        link = f"<a href='{url}' title='{title}'>{text}</a>"

    elif link_format == "text":
        link = url

    return mark_safe(link)
