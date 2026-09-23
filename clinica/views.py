from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.db import DatabaseError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AtencionForm, DuenoForm, LoginForm, MascotaForm
from .models import Atencion, Dueno, Especie, Mascota, Veterinario


class EntrarView(LoginView):
    template_name = "clinica/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True


class SalirView(LogoutView):
    pass


@login_required
def inicio(request):
    resumen = {
        "mascotas": Mascota.objects.activas().count(),
        "duenos": Dueno.objects.count(),
        "veterinarios": Veterinario.objects.filter(activo=True).count(),
        "pendientes": Atencion.objects.filter(estado=Atencion.PENDIENTE).count(),
    }
    return render(request, "clinica/inicio.html", {"resumen": resumen})


@login_required
def mascota_lista(request):
    """Listado filtrable. La vista solo coordina: el filtro vive en el manager."""
    contexto = {
        "especie_sel": request.GET.get("especie", ""),
        "dueno_sel": request.GET.get("dueno", ""),
        "texto": request.GET.get("texto", ""),
        "especies": [],
        "duenos": [],
    }
    try:
        # list() fuerza las consultas aqui dentro: un queryset es perezoso y sin
        # esto el error de base de datos estallaria al renderizar la plantilla,
        # ya fuera de este try.
        contexto["especies"] = list(Especie.objects.all())
        contexto["duenos"] = list(Dueno.objects.all())
        contexto["mascotas"] = list(
            Mascota.objects.select_related("dueno", "especie").filtrar(
                especie_id=contexto["especie_sel"] or None,
                dueno_id=contexto["dueno_sel"] or None,
                texto=contexto["texto"] or None,
            )
        )
    except DatabaseError:
        # Estado "error" de la vista: no se cae el sitio, se avisa al usuario.
        contexto["error"] = "No se pudo consultar la base de datos. Intente nuevamente."
    return render(request, "clinica/mascota_lista.html", contexto)


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


@login_required
def dueno_lista(request):
    return render(request, "clinica/dueno_lista.html", {"duenos": Dueno.objects.all()})


@login_required
def dueno_crear(request):
    form = DuenoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        dueno = form.save()
        messages.success(request, f"Dueño «{dueno.nombre_completo}» registrado.")
        return redirect("clinica:dueno_lista")
    return render(
        request, "clinica/dueno_form.html", {"form": form, "titulo": "Nuevo dueño"}
    )


@login_required
def atencion_lista(request):
    veterinario_sel = request.GET.get("veterinario", "")
    atenciones = Atencion.objects.select_related("mascota", "veterinario", "mascota__dueno")
    if veterinario_sel:
        atenciones = atenciones.filter(veterinario_id=veterinario_sel)
    return render(
        request,
        "clinica/atencion_lista.html",
        {
            "atenciones": atenciones,
            "veterinarios": Veterinario.objects.all(),
            "veterinario_sel": veterinario_sel,
        },
    )


@login_required
def atencion_crear(request):
    form = AtencionForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        atencion = form.save(commit=False)
        atencion.full_clean()  # dispara las reglas de negocio del modelo
        atencion.save()
        messages.success(request, "Atención registrada.")
        return redirect("clinica:atencion_lista")
    return render(
        request, "clinica/atencion_form.html", {"form": form, "titulo": "Nueva atención"}
    )


@login_required
def veterinario_lista(request):
    veterinarios = Veterinario.objects.prefetch_related("especies_atendidas")
    return render(request, "clinica/veterinario_lista.html", {"veterinarios": veterinarios})


@login_required
def api_mascotas_por_dueno(request, dueno_id):
    """Alimenta el desplegable dependiente del formulario de atención."""
    mascotas = Mascota.objects.activas().filter(dueno_id=dueno_id).values("id", "nombre")
    return JsonResponse({"mascotas": list(mascotas)})
