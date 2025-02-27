from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User) # admin.site.register(User)
class CustomUserAdmin(UserAdmin):
    # Pola wyświetlane na liście użytkowników
    list_display = ('email', 'user_type', 'company_name', 'is_staff', 'is_active')
    ordering = ('email',)
    search_fields = ('email', 'company_name')

    # Pola bazowe (UserAdmin) + nasze dodane
    # (None, {'fields': ('email', 'password')}) – standardowe pola do logowania
    # ('Permissions', {...}) – uprawnienia
    # ('Extra info', {...}) – przykładowa sekcja z dodatkowymi polami
    fieldsets = (
        (None, {
            'fields': ('email', 'password')
        }),
        ('Permissions', {
            'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Extra info', {
            'fields': ('user_type', 'company_name', 'company_address', 'tax_id')
        }),
    )

    # Pola używane przy dodawaniu nowego użytkownika z poziomu Admina
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active', 'is_superuser')}
        ),
    )
