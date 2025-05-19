# files/admin.py
from django.contrib import admin
from .models import File

@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ('numero', 'rango_inicial', 'rango_final', 'estado')
    list_filter = ('estado',)
    search_fields = ('numero', 'descripcion', 'observaciones')
    readonly_fields = ('creado_por', 'creado_fecha', 'modificado_por', 'modificado_fecha')
    
    def save_model(self, request, obj, form, change):
        if not change:  # Si es nuevo registro
            obj.creado_por = request.user
        else:  # Si es edición
            obj.modificado_por = request.user
        super().save_model(request, obj, form, change)