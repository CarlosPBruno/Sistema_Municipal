# files/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.file_list, name='file_list'),
    path('nuevo/', views.file_create, name='file_create'),
    path('<int:pk>/', views.file_detail, name='file_detail'),
    path('<int:pk>/editar/', views.file_update, name='file_update'),
]