from django.apps import AppConfig


class ProfilesConfig(AppConfig):
    """Configuration for the Profiles Django app."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.profiles'
    verbose_name = 'User Profiles'
    
    def ready(self):
        """Import signal handlers when the app is ready."""
        pass  # Import signals here if needed in the future
