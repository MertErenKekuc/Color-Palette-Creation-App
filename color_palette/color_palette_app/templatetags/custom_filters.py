from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(value, css_class):
    """Form alanına özel bir CSS sınıfı ekler."""
    existing_classes = value.field.widget.attrs.get('class', '')
    new_classes = f"{existing_classes} {css_class}"
    value.field.widget.attrs['class'] = new_classes.strip()
    return value