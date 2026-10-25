from django.conf import settings


def institution_context(request):
    """Provides institution branding and app configuration to all templates."""
    return {
        'INSTITUTION_NAME': getattr(settings, 'INSTITUTION_NAME', 'Curriculum Management System'),
    }
