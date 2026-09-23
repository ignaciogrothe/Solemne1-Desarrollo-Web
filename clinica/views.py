from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import get_object_or_404, redirect, render

from .forms import LoginForm, MascotaForm
from .models import Mascota


class EntrarView(LoginView):
    template_name = "clinica/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True


class SalirView(LogoutView):
    pass


@login_required
def inicio(request):
    resumen = {"mascotas": Mascota.objects.activas().count()}
    return render(request, "clinica/inicio.html", {"resumen": resumen})


@login_required
def mascota_lista(request):
    mascotas = Mascota.objects.select_related("dueno", "especie").all()
    return render(request, "clinica/mascota_lista.html", {"mascotas": mascotas})


@login_required
def mascota_detalle(request, pk):
    mascota = get_object_or_404(
        Mascota.objects.select_related("dueno", "especie"), pk=pk
    )
    atenciones = mascota.atenciones.select_related("veterinario")
    return render(
        request,
        "clinica/mascota_detalle.html",
        {"mascota": mascota, "atenciones": atenciones},
    )


@login_required
def mascota_crear(request):
    form = MascotaForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        mascota = form.save()
        messages.success(request, f"Mascota «{mascota.nombre}» registrada.")
        return redirect("clinica:mascota_lista")
    return render(
        request, "clinica/mascota_form.html", {"form": form, "titulo": "Nueva mascota"}
    )


@login_required
def mascota_editar(request, pk):
    mascota = get_object_or_404(Mascota, pk=pk)
    form = MascotaForm(request.POST or None, instance=mascota)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"Mascota «{mascota.nombre}» actualizada.")
        return redirect("clinica:mascota_lista")
    return render(
        request,
        "clinica/mascota_form.html",
        {"form": form, "titulo": f"Editar {mascota.nombre}", "objeto": mascota},
    )


@login_required
def mascota_eliminar(request, pk):
    mascota = get_object_or_404(Mascota, pk=pk)
    if request.method == "POST":
        nombre = mascota.nombre
        mascota.delete()
        messages.success(request, f"Mascota «{nombre}» eliminada.")
        return redirect("clinica:mascota_lista")
    return render(request, "clinica/mascota_confirmar_borrado.html", {"mascota": mascota})
