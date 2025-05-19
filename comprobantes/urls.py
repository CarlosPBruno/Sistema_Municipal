from django.urls import path
from . import views

urlpatterns = [
    path('', views.comprobante_list, name='comprobante_list'),
    path('nuevo/', views.comprobante_create, name='comprobante_create'),
    path('<int:pk>/', views.comprobante_detail, name='comprobante_detail'),
    path('<int:pk>/editar/', views.comprobante_update, name='comprobante_update'),
    path('exportar/', views.comprobante_export, name='comprobante_export'),
    path('cargar_excel/', views.carga_masiva_excel, name='carga_excel'),
    path('<int:pk>/pdf/', views.comprobante_pdf, name='comprobante_pdf'),
]