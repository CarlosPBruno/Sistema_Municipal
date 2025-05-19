# usuarios/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'area', 'cargo', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Información Municipal', {'fields': ('area', 'cargo', 'telefono')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información Municipal', {'fields': ('area', 'cargo', 'telefono')}),
    )

    def get_area(self, obj):
        return obj.area.nombre if obj.area else "-"
    get_area.short_description = 'Área'

    list_filter = UserAdmin.list_filter + ('area',)
    search_fields = ('username', 'first_name', 'last_name', 'email', 'area__nombre', 'cargo')