/*
 * Desplegable dependiente del formulario de atencion:
 * al elegir un dueño, el select de mascotas se repuebla con las mascotas
 * de ese dueño, consultadas a la API de la propia aplicacion.
 */

document.addEventListener("DOMContentLoaded", () => {
  const formulario = document.querySelector('form[data-validar="atencion"]');
  if (!formulario) return;

  const selectDueno = formulario.elements.dueno;
  const selectMascota = formulario.elements.mascota;
  const ayuda = document.getElementById("ayuda-mascota");
  // La URL viene del template con {% url %} usando 0 como marcador de posicion.
  const plantillaUrl = formulario.dataset.urlMascotas;

  async function cargarMascotas(duenoId) {
    selectMascota.innerHTML = '<option value="">Cargando...</option>';
    selectMascota.disabled = true;
    ayuda.textContent = "Buscando las mascotas del dueño...";

    try {
      const respuesta = await fetch(plantillaUrl.replace("/0/", `/${duenoId}/`));
      if (!respuesta.ok) throw new Error(respuesta.status);
      const datos = await respuesta.json();

      selectMascota.innerHTML = '<option value="">---------</option>';
      for (const m of datos.mascotas) {
        const opcion = new Option(m.nombre, m.id);
        selectMascota.add(opcion);
      }

      ayuda.textContent = datos.mascotas.length
        ? `${datos.mascotas.length} mascota(s) de este dueño.`
        : "Este dueño no tiene mascotas activas registradas.";
    } catch (error) {
      selectMascota.innerHTML = '<option value="">---------</option>';
      ayuda.textContent = "No se pudieron cargar las mascotas. Intente nuevamente.";
    } finally {
      selectMascota.disabled = false;
    }
  }

  selectDueno.addEventListener("change", () => {
    if (selectDueno.value) {
      cargarMascotas(selectDueno.value);
    } else {
      selectMascota.innerHTML = '<option value="">---------</option>';
      ayuda.textContent = "Elija primero un dueño para filtrar sus mascotas.";
    }
  });

  // Al editar, precargar las mascotas del dueño que ya viene seleccionado.
  if (selectDueno.value) cargarMascotas(selectDueno.value);
});
