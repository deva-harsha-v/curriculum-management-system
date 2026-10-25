from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Safely retrieves key from dictionary, trying original key, str(key), and int(key)."""
    if not isinstance(dictionary, dict):
        return None

    if key in dictionary:
        return dictionary[key]

    str_key = str(key)
    if str_key in dictionary:
        return dictionary[str_key]

    try:
        int_key = int(key)
        if int_key in dictionary:
            return dictionary[int_key]
    except (ValueError, TypeError):
        pass

    return None
