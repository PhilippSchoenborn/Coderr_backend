from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Admin configuration for Profile model."""
    list_display = ('username', 'type', 'email', 'location', 'created_at')
    list_filter = ('type', 'created_at')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'username', 'type')
        }),
        ('Personal Details', {
            'fields': ('first_name', 'last_name', 'email', 'tel')
        }),
        ('Profile Information', {
            'fields': ('file', 'location', 'description', 'working_hours')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )
