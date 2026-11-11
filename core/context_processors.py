from .models import UserPreference


CURRENCY_SYMBOLS = {
    'EUR': '€',
    'USD': '$',
    'GBP': '£',
    'MAD': 'د.م.',
}


def user_preferences(request):
    devise = 'EUR'
    format_date = 'DMY'
    if request.user.is_authenticated:
        try:
            preferences = request.user.preferences
        except UserPreference.DoesNotExist:
            preferences = None
        if preferences:
            devise = preferences.devise
            format_date = preferences.format_date
    return {
        'devise_symbole': CURRENCY_SYMBOLS[devise],
        'format_date_utilisateur': format_date,
    }
