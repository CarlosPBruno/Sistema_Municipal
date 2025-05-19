from django.contrib import admin
from .models import Proveedor, Comprobante
from django.contrib import admin
from .models import Comprobante
from .forms import ComprobanteAdminForm


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'ruc', 'telefono', 'email')
    search_fields = ('nombre', 'ruc')


@admin.register(Comprobante)
class ComprobanteAdmin(admin.ModelAdmin):
    list_display = ('nota_pago', 'expediente', 'fecha', 'proveedor', 'importe', 'estado', 'area_actual')
    list_filter = ('estado', 'area_actual', 'fecha', 'firmado')
    search_fields = ('nota_pago', 'expediente', 'proveedor__nombre', 'glosa')
    date_hierarchy = 'fecha'
    readonly_fields = ('creado_por', 'creado_fecha', 'modificado_por', 'modificado_fecha')
    form = ComprobanteAdminForm
    
    def save_model(self, request, obj, form, change):
        if not change:  # Si es nuevo registro
            obj.creado_por = request.user
        else:  # Si es edición
            obj.modificado_por = request.user
        super().save_model(request, obj, form, change)
