from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, WatchlistActivity, Report, Ban

# Register your models here.

class UserAdmin(BaseUserAdmin):
    readonly_fields = ["datetime_joined", "last_login"]
    filter_horizontal = ('user_permissions', 'groups', 'watching', 'puppets')
    list_display = ('display_name', 'password', 'color', 'datetime_joined', 'email', 'is_admin', 'is_active', 'is_superuser', 'is_staff')

    fieldsets = (
        (None, {'fields': ('display_name', 'password', 'watching', 'color', 'email', 'puppets')}),
        ('Boolean Permissions', {'fields': ('is_admin', 'is_active', 'is_superuser', 'is_staff')}),
    )

    search_fields = ('display_name', )

    ordering = ('display_name',)

admin.site.register(User, UserAdmin)
admin.site.register(WatchlistActivity)
admin.site.register(Report)
admin.site.register(Ban)