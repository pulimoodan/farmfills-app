from django import template

register = template.Library()

def float_format(value):
    return "%g" % value

register.filter('float_format', float_format)