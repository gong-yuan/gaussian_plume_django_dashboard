# from django.template.defaultfilters import register
from django import template
register = template.Library()
@register.filter(name='dict_key')
def dict_key(d, k):
    '''Returns the given key from a dictionary.'''
    # from pdb import set_trace; set_trace()
    return d[k] # d.get(k) # [k]

@register.filter
def is_in(obj, var):
    return var in obj.keys()


@register.filter
def to_title_case(d, k):
    return d[k].replace('_', ' ').title()
