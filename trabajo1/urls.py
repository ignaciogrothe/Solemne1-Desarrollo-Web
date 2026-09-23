from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    # El proyecto no conoce las rutas de la app: delega en su urls.py.
    path("", include("clinica.urls")),
]
