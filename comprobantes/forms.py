# comprobantes/forms.py
from django import forms
from .models import Comprobante, Proveedor

class ComprobanteForm(forms.ModelForm):
    class Meta:
        model = Comprobante
        fields = ['anio_eje', 'expediente', 'fecha', 'cod', 'nota_pago', 'num',
                  'proveedor', 'fuente_recurso', 'importe', 'glosa', 'folios']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'glosa': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        self.usuario = kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['nombre', 'ruc', 'direccion', 'telefono', 'email']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

class ComprobanteFilterForm(forms.Form):
    fecha_desde = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    fecha_hasta = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    proveedor = forms.ModelChoiceField(required=False, queryset=Proveedor.objects.all(), widget=forms.Select(attrs={'class': 'form-select'}))
    estado = forms.ChoiceField(required=False, choices=[('', '-- Todos --')] + list(Comprobante.ESTADO_CHOICES), widget=forms.Select(attrs={'class': 'form-select'}))
    texto = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Buscar...'}))

class CargaExcelForm(forms.Form):
    archivo = forms.FileField(label="Selecciona archivo Excel (.xlsx)")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['archivo'].widget.attrs.update({'class': 'form-control'})

class ComprobanteAdminForm(forms.ModelForm):
    class Meta:
        model = Comprobante
        exclude = ['rubro', 'tipo_recurso', 'categoria', 'fase', 'estado', 'file', 'area_actual']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

