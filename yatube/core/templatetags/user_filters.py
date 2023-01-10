from django import template

register = template.Library()


@register.filter
def addclass(field, css):
    """Добавляет в field  атрибут css"""
    return field.as_widget(attrs={'class': css})
