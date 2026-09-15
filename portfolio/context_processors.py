from .models import Profile, CustomNavLink

def profile_context(request):
    """Provides the profile instance and dynamic custom nav links globally to all templates."""
    profile = Profile.objects.first()
    custom_nav_links = list(CustomNavLink.objects.filter(is_active=True).order_by('order', 'id'))
    return {
        'profile': profile,
        'custom_nav_links': custom_nav_links,
    }
