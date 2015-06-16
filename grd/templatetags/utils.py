from django import template


register = template.Library()


@register.simple_tag(name="version")
def grd_version():
    from grd import __version__
    return __version__
