from django.urls import path

from . import views

app_name = "clinica"

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("entrar/", views.EntrarView.as_view(), name="login"),
    path("salir/", views.SalirView.as_view(), name="logout"),

    path("mascotas/", views.mascota_lista, name="mascota_lista"),
    path("mascotas/nueva/", views.mascota_crear, name="mascota_crear"),
    path("mascotas/<int:pk>/", views.mascota_detalle, name="mascota_detalle"),
    path("mascotas/<int:pk>/editar/", views.mascota_editar, name="mascota_editar"),
    path("mascotas/<int:pk>/eliminar/", views.mascota_eliminar, name="mascota_eliminar"),
]
