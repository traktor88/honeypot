try:
    from functools import wraps
except ImportError:
    from django.utils.functional import wraps # Python <= 2.4

from django.conf import settings
from django.http import HttpResponseBadRequest

def honeypot_equals(val):
    expected = getattr(settings, 'HONEYPOT_VALUE', '')
    if callable(expected):
        expected = callable()
    return val == expected

def verify_honeypot_value(request, field_name):
    verifier = getattr(settings, 'HONEYPOT_VERIFIER', honeypot_equals)
    if request.method == 'POST':
        field = field_name or settings.HONEYPOT_FIELD_NAME
        if field not in request.POST or not verifier(request.POST[field]):
            return HttpResponseBadRequest('Honeypot Error')

def check_honeypot(func=None, field_name=None):
    def inner(request, *args, **kwargs):
        response = verify_honeypot_value(request, field_name)
        if response:
            return response
        else:
            return func(request, *args, **kwargs)
    inner = wraps(func)(inner)

    if func is None:
        def decorator(func):
            return inner
        return decorator
    return inner
