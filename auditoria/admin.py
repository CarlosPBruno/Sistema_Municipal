# auditoria/admin.py
from django.contrib import admin
from .models import LogAuditoria

@admin.register(LogAuditoria)
class LogAuditoriaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'fecha_hora', 'accion', 'content_type', 'object_id', 'ip_address')
    list_filter = ('accion', 'fecha_hora', 'usuario', 'content_type')
    search_fields = ('descripcion', 'usuario__username', 'ip_address')
    readonly_fields = ('usuario', 'fecha_hora', 'accion', 'content_type', 'object_id', 
                      'descripcion', 'datos_anteriores', 'datos_nuevos', 'ip_address')
    
    def has_add_permission(self, request):
        return False  # Nadie puede añadir logs manualmente
    
    def has_change_permission(self, request, obj=None):
        return False  # Nadie puede modificar logs