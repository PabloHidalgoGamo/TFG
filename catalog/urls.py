from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('clases/', views.clase_list, name='clase_list'),
    path('clases/<int:clase_id>/', views.clase_detail, name='clase_detail'),
    path('reservar/<uuid:claseinstancia_id>/', views.reservar_clase, name='reservar_clase'),
    path('mis_reservas/', views.mis_reservas, name='mis_reservas'),
    path('cancelar/<uuid:claseinstancia_id>/', views.cancelar_reserva, name='cancelar_reserva'),

    path('profesor/clases/', views.gestionar_clases, name='gestionar_clases'),
    path('profesor/reservas/', views.ver_reservas_profesor, name='ver_reservas_profesor'),
    path('profesor/horarios/', views.gestionar_horarios, name='gestionar_horarios'),

    path('registro/', views.registro, name='registro'),

    path('perfil/', views.perfil_usuario, name='perfil_usuario'),
]