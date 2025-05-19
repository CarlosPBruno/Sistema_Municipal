# comprobantes/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
import csv
from datetime import datetime
from .models import Comprobante, Proveedor
from .forms import ComprobanteForm, ProveedorForm, ComprobanteFilterForm
from auditoria.models import LogAuditoria
from django.contrib.contenttypes.models import ContentType
from .forms import CargaExcelForm 
from django.http import FileResponse
from reportlab.pdfgen import canvas
import io

@login_required
def comprobante_list(request):
    form = ComprobanteFilterForm(request.GET)
    comprobantes = Comprobante.objects.all()
    if not request.user.is_superuser:
        comprobantes = comprobantes.filter(area_actual=request.user.area)


    # Aplicar filtros si hay parámetros
    if form.is_valid():
        if form.cleaned_data.get('fecha_desde'):
            comprobantes = comprobantes.filter(fecha__gte=form.cleaned_data['fecha_desde'])
        if form.cleaned_data.get('fecha_hasta'):
            comprobantes = comprobantes.filter(fecha__lte=form.cleaned_data['fecha_hasta'])
        if form.cleaned_data.get('proveedor'):
            comprobantes = comprobantes.filter(proveedor=form.cleaned_data['proveedor'])
        if form.cleaned_data.get('estado'):
            comprobantes = comprobantes.filter(estado=form.cleaned_data['estado'])
        if form.cleaned_data.get('texto'):
            texto = form.cleaned_data['texto']
            comprobantes = comprobantes.filter(
                Q(nota_pago__icontains=texto) | 
                Q(glosa__icontains=texto) | 
                Q(expediente__icontains=texto) | 
                Q(proveedor__nombre__icontains=texto)
            )
    
    # Paginación
    paginator = Paginator(comprobantes, 20)  # 20 comprobantes por página
    page = request.GET.get('page')
    comprobantes_paginados = paginator.get_page(page)
    
    # Registrar visualización en auditoría
    LogAuditoria.objects.create(
        usuario=request.user,
        accion='ver',
        content_type=ContentType.objects.get_for_model(Comprobante),
        object_id=0,  # 0 indica visualización de lista
        descripcion=f"Usuario {request.user} visualizó la lista de comprobantes con filtros: {request.GET}",
        ip_address=get_client_ip(request)
    )
    
    return render(request, 'comprobantes/comprobante_list.html', {
        'comprobantes': comprobantes_paginados,
        'form': form,
    })

@login_required
def comprobante_create(request):
    if request.method == 'POST':
        form = ComprobanteForm(request.POST, usuario=request.user)
        if form.is_valid():
            comprobante = form.save(commit=False)
            comprobante.creado_por = request.user
            comprobante.area_actual = request.user.area
            comprobante.save()
            
            # Registrar en auditoría
            LogAuditoria.objects.create(
                usuario=request.user,
                accion='crear',
                content_type=ContentType.objects.get_for_model(Comprobante),
                object_id=comprobante.id,
                descripcion=f"Usuario {request.user} creó el comprobante {comprobante}",
                datos_nuevos={field: str(getattr(comprobante, field)) for field in form.fields},
                ip_address=get_client_ip(request)
            )
            
            messages.success(request, f'Comprobante {comprobante.nota_pago} creado exitosamente.')
            return redirect('comprobante_detail', pk=comprobante.pk)
    else:
        form = ComprobanteForm(usuario=request.user)
    
    return render(request, 'comprobantes/comprobante_form.html', {
        'form': form,
        'titulo': 'Crear Nuevo Comprobante'
    })

@login_required
def comprobante_detail(request, pk):
    comprobante = get_object_or_404(Comprobante, pk=pk)
    
    # Registrar visualización en auditoría
    LogAuditoria.objects.create(
        usuario=request.user,
        accion='ver',
        content_type=ContentType.objects.get_for_model(Comprobante),
        object_id=comprobante.id,
        descripcion=f"Usuario {request.user} visualizó el comprobante {comprobante}",
        ip_address=get_client_ip(request)
    )
    
    return render(request, 'comprobantes/comprobante_detail.html', {
        'comprobante': comprobante
    })

@login_required
def comprobante_update(request, pk):
    comprobante = get_object_or_404(Comprobante, pk=pk)
    datos_anteriores = {field: str(getattr(comprobante, field)) for field in ComprobanteForm.Meta.fields}
    
    if request.method == 'POST':
        form = ComprobanteForm(request.POST, instance=comprobante, usuario=request.user)
        if form.is_valid():
            comprobante = form.save(commit=False)
            comprobante.modificado_por = request.user
            comprobante.save()
            
            # Registrar en auditoría
            datos_nuevos = {field: str(getattr(comprobante, field)) for field in form.fields}
            LogAuditoria.objects.create(
                usuario=request.user,
                accion='editar',
                content_type=ContentType.objects.get_for_model(Comprobante),
                object_id=comprobante.id,
                descripcion=f"Usuario {request.user} modificó el comprobante {comprobante}",
                datos_anteriores=datos_anteriores,
                datos_nuevos=datos_nuevos,
                ip_address=get_client_ip(request)
            )
            
            messages.success(request, f'Comprobante {comprobante.nota_pago} actualizado exitosamente.')
            return redirect('comprobante_detail', pk=comprobante.pk)
    else:
        form = ComprobanteForm(instance=comprobante, usuario=request.user)
    
    return render(request, 'comprobantes/comprobante_form.html', {
        'form': form,
        'comprobante': comprobante,
        'titulo': f'Editar Comprobante {comprobante.nota_pago}'
    })

@login_required
def comprobante_export(request):
    # Obtener los mismos filtros que en la lista
    form = ComprobanteFilterForm(request.GET)
    comprobantes = Comprobante.objects.all()
    
    if form.is_valid():
        if form.cleaned_data.get('fecha_desde'):
            comprobantes = comprobantes.filter(fecha__gte=form.cleaned_data['fecha_desde'])
        if form.cleaned_data.get('fecha_hasta'):
            comprobantes = comprobantes.filter(fecha__lte=form.cleaned_data['fecha_hasta'])
        if form.cleaned_data.get('proveedor'):
            comprobantes = comprobantes.filter(proveedor=form.cleaned_data['proveedor'])
        if form.cleaned_data.get('estado'):
            comprobantes = comprobantes.filter(estado=form.cleaned_data['estado'])
        if form.cleaned_data.get('texto'):
            texto = form.cleaned_data['texto']
            comprobantes = comprobantes.filter(
                Q(nota_pago__icontains=texto) | 
                Q(glosa__icontains=texto) | 
                Q(expediente__icontains=texto) | 
                Q(proveedor__nombre__icontains=texto)
            )
    
    # Crear respuesta CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="comprobantes_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    # Escribir encabezados
    writer.writerow(['Año', 'Expediente', 'Fecha', 'Cod', 'Nota Pago', 'Num', 'Proveedor', 
                     'Fte-Tr', 'Importe', 'Glosa', 'Folios', 'Estado', 'File'])
    
    # Escribir datos
    for comp in comprobantes:
        writer.writerow([
            comp.anio_eje,
            comp.expediente,
            comp.fecha.strftime('%d/%m/%Y'),
            comp.cod,
            comp.nota_pago,
            comp.num,
            comp.proveedor.nombre,
            comp.fuente_recurso,
            float(comp.importe),
            comp.glosa,
            comp.folios or '',
            comp.get_estado_display(),
            comp.file.numero if comp.file else ''
        ])
    
    # Registrar exportación en auditoría
    LogAuditoria.objects.create(
        usuario=request.user,
        accion='exportar',
        content_type=ContentType.objects.get_for_model(Comprobante),
        object_id=0,
        descripcion=f"Usuario {request.user} exportó comprobantes a CSV con filtros: {request.GET}",
        ip_address=get_client_ip(request)
    )
    
    return response

@login_required
def carga_masiva_excel(request):
    if request.method == 'POST':
        form = CargaExcelForm(request.POST, request.FILES)
        if form.is_valid():
            archivo_excel = request.FILES['archivo']
            df = pd.read_excel(archivo_excel)

            # Recorremos el Excel y guardamos comprobantes
            for index, row in df.iterrows():
                try:
                    proveedor, _ = Proveedor.objects.get_or_create(
                        nombre=row['Proveedor'].strip()
                    )

                    Comprobante.objects.create(
                        anio_eje=str(row['Año']),
                        expediente=row['Expediente'],
                        fecha=pd.to_datetime(row['Fecha']).date(),
                        cod=row['Cod'],
                        nota_pago=row['NotaPago'],
                        num=row['Num'],
                        proveedor=proveedor,
                        fuente_recurso=row['Fte-Tr'],
                        importe=row['Importe'],
                        glosa=row['Glosa'],
                        folios=row.get('Folios', None),
                        firmado=False,
                        rubro=row.get('Rubro', '00 RECURSOS ORDINARIOS'),
                        tipo_recurso=row.get('Tipo Recurso', '0'),
                        categoria=row.get('Categoria', 'GASTO CAPITAL'),
                        fase=row.get('Fase', 'GIRADO'),
                        creado_por=request.user,
                        modificado_por=request.user,
                        area_actual=request.user.area,
                    )
                except Exception as e:
                    print(f"Error en fila {index + 2}: {e}")
                    continue

            messages.success(request, 'Carga masiva completada correctamente.')
            return redirect('comprobante_list')
    else:
        form = CargaExcelForm()

    return render(request, 'comprobantes/carga_excel.html', {'form': form})

def comprobante_pdf(request, pk):
    comprobante = get_object_or_404(Comprobante, pk=pk)

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    p.drawString(100, 800, f"Comprobante: {comprobante.nota_pago}")
    p.drawString(100, 780, f"Proveedor: {comprobante.proveedor.nombre}")
    p.drawString(100, 760, f"Importe: S/. {comprobante.importe}")
    p.drawString(100, 740, f"Glosa: {comprobante.glosa}")
    p.showPage()
    p.save()

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f'comprobante_{comprobante.id}.pdf')


# Función auxiliar para obtener IP del cliente
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
