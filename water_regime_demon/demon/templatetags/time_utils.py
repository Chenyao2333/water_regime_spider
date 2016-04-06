from django import template
register = template.Library()


@register.filter
def to_datetime(ts):
    if ts:
        import datetime
        return datetime.datetime.fromtimestamp(float(ts))
    else:
        return None
