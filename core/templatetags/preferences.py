from datetime import datetime
from decimal import Decimal, InvalidOperation

from django import template
from django.utils import timezone

from core.context_processors import CURRENCY_SYMBOLS
from core.models import UserPreference


register = template.Library()


def _user_preference(context):
    request = context.get('request')
    if request and request.user.is_authenticated:
        try:
            return request.user.preferences
        except UserPreference.DoesNotExist:
            pass
    return None


@register.simple_tag(takes_context=True)
def money(context, value):
    preference = _user_preference(context)
    devise = preference.devise if preference else 'EUR'
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        amount = Decimal('0')
    # Keep French number grouping while applying the user's chosen currency.
    formatted = format(amount, ',.2f').replace(',', '\0').replace('.', ',').replace('\0', '\u202f')
    return f"{formatted}\u00a0{CURRENCY_SYMBOLS[devise]}"


@register.simple_tag(takes_context=True)
def user_date(context, value):
    if value is None:
        return '—'
    preference = _user_preference(context)
    format_code = preference.format_date if preference else 'DMY'
    patterns = {'DMY': '%d/%m/%Y', 'MDY': '%m/%d/%Y', 'ISO': '%Y-%m-%d'}
    if isinstance(value, datetime):
        if timezone.is_aware(value):
            value = timezone.localtime(value)
        return value.strftime(patterns[format_code] + ' à %H:%M')
    return value.strftime(patterns[format_code])
