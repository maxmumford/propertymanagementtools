from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
def joinby(iterable, args):
    join_string = object_property_name = None
    if '|' in args:
        join_string, object_property_name = args.split('|')
    else:
        join_string = args
    if object_property_name:
        iterable = [getattr(prop, object_property_name) for prop in iterable]
    return join_string.join(iterable)
