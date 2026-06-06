from django import template

register = template.Library()

COUNTRY_FLAGS = {
    'United States': '🇺🇸',
    'USA': '🇺🇸',
    'United Kingdom': '🇬🇧',
    'UK': '🇬🇧',
    'Canada': '🇨🇦',
    'Australia': '🇦🇺',
    'Germany': '🇩🇪',
    'France': '🇫🇷',
    'Spain': '🇪🇸',
    'Italy': '🇮🇹',
    'Netherlands': '🇳🇱',
    'Belgium': '🇧🇪',
    'Switzerland': '🇨🇭',
    'Austria': '🇦🇹',
    'Ireland': '🇮🇪',
    'Sweden': '🇸🇪',
    'Norway': '🇳🇴',
    'Denmark': '🇩🇰',
    'Finland': '🇫🇮',
    'Poland': '🇵🇱',
    'Czech Republic': '🇨🇿',
    'Hungary': '🇭🇺',
    'Romania': '🇷🇴',
    'Bulgaria': '🇧🇬',
    'Greece': '🇬🇷',
    'Portugal': '🇵🇹',
    'Turkey': '🇹🇷',
    'Russia': '🇷🇺',
    'Ukraine': '🇺🇦',
    'India': '🇮🇳',
    'China': '🇨🇳',
    'Japan': '🇯🇵',
    'South Korea': '🇰🇷',
    'Singapore': '🇸🇬',
    'Hong Kong': '🇭🇰',
    'Taiwan': '🇹🇼',
    'Thailand': '🇹🇭',
    'Vietnam': '🇻🇳',
    'Malaysia': '🇲🇾',
    'Indonesia': '🇮🇩',
    'Philippines': '🇵🇭',
    'Brazil': '🇧🇷',
    'Argentina': '🇦🇷',
    'Mexico': '🇲🇽',
    'Colombia': '🇨🇴',
    'Chile': '🇨🇱',
    'Peru': '🇵🇪',
    'South Africa': '🇿🇦',
    'Egypt': '🇪🇬',
    'Nigeria': '🇳🇬',
    'Kenya': '🇰🇪',
    'Morocco': '🇲🇦',
    'New Zealand': '🇳🇿',
}

@register.filter
def country_flag(country_name):
    return COUNTRY_FLAGS.get(country_name, '🌐')

@register.filter
def duration_format(seconds):
    if not seconds:
        return '0s'
    seconds = int(seconds)
    if seconds < 60:
        return f'{seconds}s'
    elif seconds < 3600:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f'{minutes}m {remaining_seconds}s'
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f'{hours}h {minutes}m'
