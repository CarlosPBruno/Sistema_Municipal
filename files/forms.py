# files/forms.py
from django import forms
from .models import File

class FileForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ['numero', 'descripcion', 'rango_inicial', 'rango_final', 'faltantes', 'estado', 'observaciones']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
            'faltantes': forms.Textarea(attrs={'rows': 2}),
            'observaciones': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        self.usuario = kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})