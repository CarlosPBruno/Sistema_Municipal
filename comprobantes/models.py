# comprobantes/models.py
from django.db import models
from django.conf import settings
from areas.models import Area

class Proveedor(models.Model):
    nombre = models.CharField(max_length=200)
    ruc = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'
        ordering = ['nombre']

class Comprobante(models.Model):
    ESTADO_CHOICES = (
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
        ('anulado', 'Anulado'),
    )
    
    # Campos según tu Excel
    anio_eje = models.CharField(max_length=4, verbose_name='Año Ejecución')
    expediente = models.CharField(max_length=20)
    fecha = models.DateField()
    cod = models.CharField(max_length=10)
    nota_pago = models.CharField(max_length=10, verbose_name='Nota de Pago')
    num = models.CharField(max_length=30, verbose_name='Número')
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT, related_name='comprobantes')
    fuente_recurso = models.CharField(max_length=10, verbose_name='Fuente-Tr')
    importe = models.DecimalField(max_digits=12, decimal_places=2)
    glosa = models.TextField()
    folios = models.IntegerField(blank=True, null=True)
    firmado = models.BooleanField(default=False)
    
    # Campos adicionales
    rubro = models.CharField(max_length=100, default='00 RECURSOS ORDINARIOS')
    tipo_recurso = models.CharField(max_length=50, default='0')
    categoria = models.CharField(max_length=100, default='GASTO CAPITAL')
    fase = models.CharField(max_length=50, default='GIRADO')
    
    # Control y seguimiento
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    file = models.ForeignKey('files.File', on_delete=models.SET_NULL, null=True, blank=True, related_name='comprobantes')
    
    # Auditoría
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='comprobantes_creados')
    creado_fecha = models.DateTimeField(auto_now_add=True)
    modificado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='comprobantes_modificados', null=True, blank=True)
    modificado_fecha = models.DateTimeField(auto_now=True)
    area_actual = models.ForeignKey(Area, on_delete=models.PROTECT, related_name='comprobantes_actuales')
    
    def __str__(self):
        return f"{self.nota_pago} - {self.proveedor.nombre} (S/.{self.importe})"
    
    class Meta:
        verbose_name = 'Comprobante'
        verbose_name_plural = 'Comprobantes'
        ordering = ['-fecha', 'nota_pago']