from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, WatchlistActivity, Report

# Register your models here.

class UserAdmin(BaseUserAdmin):
    readonly_fields = ["date_joined", "last_login"]
    filter_horizontal = ('user_permissions', 'groups', 'watching', 'puppets')
    list_display = ('display_name', 'password', 'color', 'email', 'is_admin', 'is_active', 'is_superuser', 'is_staff')

    fieldsets = (
        (None, {'fields': ('display_name', 'password', 'watching', 'color', 'email', 'puppets')}),
        ('Boolean Permissions', {'fields': ('is_admin', 'is_active', 'is_superuser', 'is_staff')}),
    )

    ordering = ('display_name',)

admin.site.register(User, UserAdmin)
admin.site.register(WatchlistActivity)
admin.site.register(Report)