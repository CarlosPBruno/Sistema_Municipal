# files/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import File
from .forms import FileForm
from comprobantes.models import Comprobante
from auditoria.models import LogAuditoria
from django.contrib.contenttypes.models import ContentType

@login_required
def file_list(request):
    query = request.GET.get('q', '')
    files = File.objects.all()
    
    if query:
        files = files.filter(
            Q(numero__icontains=query) | 
            Q(descripcion__icontains=query) |
            Q(observaciones__icontains=query)
        )
    
    paginator = Paginator(files, 20)
    page = request.GET.get('page')
    files_paginated = paginator.get_page(page)
    
    # Registrar visualización en auditoría
    LogAuditoria.objects.create(
        usuario=request.user,
        accion='ver',
        content_type=ContentType.objects.get_for_model(File),
        object_id=0,
        descripcion=f"Usuario {request.user} visualizó la lista de files",
        ip_address=get_client_ip(request)
    )
    
    return render(request, 'files/file_list.html', {
        'files': files_paginated,
        'query': query
    })

@login_required
def file_create(request):
    if request.method == 'POST':
        form = FileForm(request.POST, usuario=request.user)
        if form.is_valid():
            file = form.save(commit=False)
            file.creado_por = request.user
            file.save()
            
            # Registrar en auditoría
            LogAuditoria.objects.create(
                usuario=request.user,
                accion='crear',
                content_type=ContentType.objects.get_for_model(File),
                object_id=file.id,
                descripcion=f"Usuario {request.user} creó el file {file}",
                datos_nuevos={field: str(getattr(file, field)) for field in form.fields},
                ip_address=get_client_ip(request)
            )
            
            messages.success(request, f'File {file.numero} creado exitosamente.')
            return redirect('file_detail', pk=file.pk)
    else:
        form = FileForm(usuario=request.user)
    
    return render(request, 'files/file_form.html', {
        'form': form,
        'titulo': 'Crear Nuevo File'
    })

@login_required
def file_detail(request, pk):
    file = get_object_or_404(File, pk=pk)
    # Obtener comprobantes asociados a este file
    comprobantes = Comprobante.objects.filter(file=file).order_by('nota_pago')
    
    # Determinar si hay comprobantes faltantes según el rango
    inicio = int(file.rango_inicial.split('/')[-1])
    fin = int(file.rango_final.split('/')[-1])
    numeros_esperados = set(range(inicio, fin + 1))
    
    numeros_existentes = set(
        int(c.nota_pago.split('/')[-1]) 
        for c in comprobantes 
        if c.nota_pago and c.nota_pago.split('/')[-1].isdigit()
    )
    
    faltantes = numeros_esperados - numeros_existentes
    faltantes = sorted(faltantes)
    
    # Registrar visualización en auditoría
    LogAuditoria.objects.create(
        usuario=request.user,
        accion='ver',
        content_type=ContentType.objects.get_for_model(File),
        object_id=file.id,
        descripcion=f"Usuario {request.user} visualizó el file {file}",
        ip_address=get_client_ip(request)
    )
    
    return render(request, 'files/file_detail.html', {
        'file': file,
        'comprobantes': comprobantes,
        'faltantes': faltantes,
        'total_comprobantes': comprobantes.count(),
        'comprobantes_esperados': len(numeros_esperados)
    })

@login_required
def file_update(request, pk):
    file = get_object_or_404(File, pk=pk)
    datos_anteriores = {field: str(getattr(file, field)) for field in FileForm.Meta.fields}
    
    if request.method == 'POST':
        form = FileForm(request.POST, instance=file, usuario=request.user)
        if form.is_valid():
            file = form.save(commit=False)
            file.modificado_por = request.user
            file.save()
            
            # Registrar en auditoría
            datos_nuevos = {field: str(getattr(file, field)) for field in form.fields}
            LogAuditoria.objects.create(
                usuario=request.user,
                accion='editar',
                content_type=ContentType.objects.get_for_model(File),
                object_id=file.id,
                descripcion=f"Usuario {request.user} modificó el file {file}",
                datos_anteriores=datos_anteriores,
                datos_nuevos=datos_nuevos,
                ip_address=get_client_ip(request)
            )
            
            messages.success(request, f'File {file.numero} actualizado exitosamente.')
            return redirect('file_detail', pk=file.pk)
    else:
        form = FileForm(instance=file, usuario=request.user)
    
    return render(request, 'files/file_form.html', {
        'form': form,
        'file': file,
        'titulo': f'Editar File {file.numero}'
    })

# Función auxiliar para obtener IP del cliente
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip