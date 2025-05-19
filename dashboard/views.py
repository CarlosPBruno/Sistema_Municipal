# dashboard/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from comprobantes.models import Comprobante
from files.models import File

@login_required
def home(request):
    # Estadísticas generales
    total_comprobantes = Comprobante.objects.count()
    total_importe = Comprobante.objects.aggregate(total=Sum('importe'))['total'] or 0
    
    # Comprobantes recientes (últimos 30 días)
    fecha_inicio = timezone.now().date() - timedelta(days=30)
    comprobantes_recientes = Comprobante.objects.filter(fecha__gte=fecha_inicio).count()
    
    # Comprobantes por estado
    comprobantes_por_estado = Comprobante.objects.values('estado').annotate(
        total=Count('id')).order_by('estado')
    
    # Files por estado
    files_por_estado = File.objects.values('estado').annotate(
        total=Count('id')).order_by('estado')
    
    # Comprobantes pendientes
    comprobantes_pendientes = Comprobante.objects.filter(
        estado='pendiente').order_by('-fecha')[:10]
    
    # Comprobantes recientes del usuario
    mis_comprobantes = Comprobante.objects.filter(
        creado_por=request.user).order_by('-creado_fecha')[:5]
    
    return render(request, 'dashboard/home.html', {
        'total_comprobantes': total_comprobantes,
        'total_importe': total_importe,
        'comprobantes_recientes': comprobantes_recientes,
        'comprobantes_por_estado': comprobantes_por_estado,
        'files_por_estado': files_por_estado,
        'comprobantes_pendientes': comprobantes_pendientes,
        'mis_comprobantes': mis_comprobantes,
    })