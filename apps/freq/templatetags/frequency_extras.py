from django import template
register = template.Library()


@register.filter
def multiply(value, arg):
    arg = float(arg)
    return int(value * arg)


@register.filter
def significantDigits(value, arg):
    arg = int(arg)
    formatter = '%0.' + str(arg) + 'g'
    return float(formatter % (value,))


