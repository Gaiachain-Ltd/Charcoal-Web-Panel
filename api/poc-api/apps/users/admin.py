from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as CoreUserAdmin
from django.contrib.auth.forms import UserChangeForm as CoreUserChangeForm
from django.utils.translation import ugettext_lazy as _

from apps.users.models import Role

User = get_user_model()


class UserAdmin(CoreUserAdmin):
    form = CoreUserChangeForm
    ordering = ('email',)
    list_display = ('email', 'role')
    list_filter = ('email', 'role')
    search_fields = ('email',)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'function', 'code', 'contact')}),
        (_('Other data'), {'fields': ('role',)}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
    )


admin.site.register(User, UserAdmin)
admin.site.register(Role)

