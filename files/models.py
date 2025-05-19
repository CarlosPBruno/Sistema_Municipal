# files/models.py
from django.db import models
from django.conf import settings

class File(models.Model):
    ESTADO_CHOICES = (
        ('pendiente', 'Pendiente'),
        ('completo', 'Completo'),
        ('incompleto', 'Incompleto'),
    )
    
    numero = models.CharField(max_length=10, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    rango_inicial = models.CharField(max_length=10, verbose_name='Del Comp. Pago')
    rango_final = models.CharField(max_length=10, verbose_name='Al Comp. Pago')
    faltantes = models.TextField(blank=True, null=True, verbose_name='Comprobantes Faltantes')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    observaciones = models.TextField(blank=True, null=True)
    
    # Auditoría
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='files_creados')
    creado_fecha = models.DateTimeField(auto_now_add=True)
    modificado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='files_modificados', null=True, blank=True)
    modificado_fecha = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"File {self.numero}: {self.rango_inicial} - {self.rango_final}"
    
    class Meta:
        verbose_name = 'File'
        verbose_name_plural = 'Files'
        ordering = ['numero']