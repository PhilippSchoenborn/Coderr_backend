"""
Business logic for profiles app.
Extracts business logic from views to separate concerns.
"""
from .models import Profile


class ProfileBusinessLogic:
    """Business logic for profile operations."""
    
    @staticmethod
    def check_profile_ownership(profile, user):
        """Check if user owns the profile."""
        return profile.user == user
    
    @staticmethod
    def update_user_email(profile, email):
        """Update user's email address."""
        if profile.user:
            profile.user.email = email
            profile.user.save()
    
    @staticmethod
    def get_profile_response_data(profile):
        """Convert profile to response data format."""
        try:
            return {
                'user': profile.user.id if profile.user else None,
                'username': profile.username,
                'first_name': profile.first_name or '',
                'last_name': profile.last_name or '',
                'file': profile.file.name if profile.file else None,
                'location': profile.location or '',
                'tel': profile.tel or '',
                'description': profile.description or '',
                'working_hours': profile.working_hours or '',
                'type': profile.type,
                'email': profile.user.email if profile.user else '',
                'created_at': profile.created_at,
            }
        except Exception:
            return None
    
    @staticmethod
    def get_profile_list_data(profile):
        """Convert profile to list format."""
        return {
            'user': profile.user.id if profile.user else None,
            'username': profile.username,
            'first_name': profile.first_name or '',
            'last_name': profile.last_name or '',
            'location': profile.location or '',
            'tel': profile.tel or '',
            'description': profile.description or '',
            'working_hours': profile.working_hours or '',
            'file': profile.file.name if profile.file else None,
            'type': profile.type
        }
    
    @staticmethod
    def filter_profiles_by_type(queryset, profile_type):
        """Filter profiles by type."""
        if profile_type in ['customer', 'business']:
            return queryset.filter(type=profile_type)
        return queryset
