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

    path("duenos/", views.dueno_lista, name="dueno_lista"),
    path("duenos/nuevo/", views.dueno_crear, name="dueno_crear"),

    path("atenciones/", views.atencion_lista, name="atencion_lista"),
    path("atenciones/nueva/", views.atencion_crear, name="atencion_crear"),

    path("veterinarios/", views.veterinario_lista, name="veterinario_lista"),

    path("api/duenos/<int:dueno_id>/mascotas/", views.api_mascotas_por_dueno, name="api_mascotas"),
]
