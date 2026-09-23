from django.contrib import admin

from .models import Atencion, Dueno, Especie, Mascota, Veterinario


@admin.register(Mascota)
class MascotaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "especie", "dueno", "sexo", "peso_kg", "activa")
    list_filter = ("especie", "sexo", "activa")
    search_fields = ("nombre", "dueno__nombre", "dueno__apellido", "dueno__rut")
    list_editable = ("activa",)
    ordering = ("nombre",)


@admin.register(Dueno)
class DuenoAdmin(admin.ModelAdmin):
    list_display = ("rut", "nombre", "apellido", "email", "telefono", "cantidad_mascotas")
    list_filter = ("fecha_registro",)
    search_fields = ("rut", "nombre", "apellido", "email")
    ordering = ("apellido", "nombre")


@admin.register(Atencion)
class AtencionAdmin(admin.ModelAdmin):
    list_display = ("fecha", "mascota", "veterinario", "motivo", "costo_neto", "estado")
    list_filter = ("estado", "veterinario", "fecha")
    search_fields = ("motivo", "diagnostico", "mascota__nombre")
    list_editable = ("estado",)
    date_hierarchy = "fecha"


@admin.register(Veterinario)
class VeterinarioAdmin(admin.ModelAdmin):
    list_display = ("apellido", "nombre", "especialidad", "email", "activo")
    list_filter = ("activo", "especies_atendidas")
    search_fields = ("nombre", "apellido", "especialidad")
    filter_horizontal = ("especies_atendidas",)


@admin.register(Especie)
class EspecieAdmin(admin.ModelAdmin):
    list_display = ("nombre", "nombre_cientifico")
    search_fields = ("nombre", "nombre_cientifico")
    ordering = ("nombre",)
