# blog/templatetags/split_filters.py

from django import template

register = template.Library()

@register.filter
def split(value, delimiter=","):
    """Splits a string by the given delimiter."""
    if value:
        return [item.strip() for item in value.split(delimiter)]
    return []
