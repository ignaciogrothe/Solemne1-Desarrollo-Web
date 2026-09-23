/*
 * Validacion de formularios en el cliente.
 *
 * Cada formulario declara en el HTML a que conjunto de reglas pertenece
 * (data-validar="login"). Aqui se define ese conjunto: por cada campo, una
 * lista de validadores. Un validador devuelve null si el valor esta bien,
 * o el mensaje de error en español si esta mal.
 *
 * La validacion del navegador NO reemplaza la del servidor: los modelos
 * mantienen sus propias restricciones.
 */

// ---------- Validadores reutilizables (uno por tipo de regla) ----------

// Recibe el mensaje completo porque en español el adjetivo concuerda en
// género con el campo ("obligatorio" / "obligatoria").
const requerido = (mensaje) => (valor) => (valor.trim() === "" ? mensaje : null);

const seleccionObligatoria = (etiqueta) => (valor) =>
  valor === "" ? `Debe seleccionar ${etiqueta}.` : null;

const largoMinimo = (n, etiqueta) => (valor) =>
  valor.trim().length > 0 && valor.trim().length < n
    ? `${etiqueta} debe tener al menos ${n} caracteres.`
    : null;

const largoMaximo = (n, etiqueta) => (valor) =>
  valor.trim().length > n
    ? `${etiqueta} no puede superar los ${n} caracteres.`
    : null;

const formatoEmail = (valor) =>
  valor.trim() !== "" && !/^[^\s@]+@[^\s@]+\.[a-z]{2,}$/i.test(valor.trim())
    ? "Ingrese un correo válido, por ejemplo nombre@dominio.cl."
    : null;

const formatoTelefono = (valor) =>
  valor.trim() !== "" && !/^\+?56?\s?9\d{8}$/.test(valor.replace(/[\s.-]/g, ""))
    ? "Ingrese un teléfono chileno válido, por ejemplo +56912345678."
    : null;

const rangoNumerico = (min, max, etiqueta) => (valor) => {
  if (valor.trim() === "") return null;
  const numero = Number(valor);
  if (Number.isNaN(numero)) return `${etiqueta} debe ser un número.`;
  if (numero < min || numero > max)
    return `${etiqueta} debe estar entre ${min} y ${max}.`;
  return null;
};

const fechaNoFutura = (etiqueta) => (valor) => {
  if (valor === "") return null;
  const hoy = new Date().toISOString().slice(0, 10);
  return valor > hoy ? `${etiqueta} no puede ser posterior a hoy.` : null;
};

// Digito verificador de RUT chileno (modulo 11), igual que en el modelo.
const formatoRut = (valor) => {
  const limpio = valor.replace(/[.\-]/g, "").toUpperCase();
  if (limpio === "") return null;
  if (!/^\d{7,8}[0-9K]$/.test(limpio))
    return "El RUT debe tener el formato 12345678-9.";

  const cuerpo = limpio.slice(0, -1);
  const digito = limpio.slice(-1);
  let suma = 0;
  let factor = 2;
  for (let i = cuerpo.length - 1; i >= 0; i--) {
    suma += Number(cuerpo[i]) * factor;
    factor = factor === 7 ? 2 : factor + 1;
  }
  const resto = 11 - (suma % 11);
  const esperado = resto === 11 ? "0" : resto === 10 ? "K" : String(resto);
  return digito !== esperado ? "El dígito verificador del RUT no es correcto." : null;
};

// ---------- Reglas por formulario ----------

const REGLAS = {
  login: {
    username: [requerido("El usuario es obligatorio."), largoMinimo(3, "El usuario")],
    password: [requerido("La contraseña es obligatoria."), largoMinimo(4, "La contraseña")],
  },
  mascota: {
    nombre: [
      requerido("El nombre es obligatorio."),
      largoMinimo(2, "El nombre"),
      largoMaximo(60, "El nombre"),
    ],
    dueno: [seleccionObligatoria("un dueño")],
    especie: [seleccionObligatoria("una especie")],
    sexo: [seleccionObligatoria("el sexo")],
    fecha_nacimiento: [
      requerido("La fecha de nacimiento es obligatoria."),
      fechaNoFutura("La fecha de nacimiento"),
    ],
    peso_kg: [requerido("El peso es obligatorio."), rangoNumerico(0.1, 200, "El peso")],
  },
  dueno: {
    rut: [requerido("El RUT es obligatorio."), formatoRut],
    nombre: [requerido("El nombre es obligatorio."), largoMinimo(2, "El nombre")],
    apellido: [requerido("El apellido es obligatorio."), largoMinimo(2, "El apellido")],
    email: [requerido("El correo es obligatorio."), formatoEmail],
    telefono: [requerido("El teléfono es obligatorio."), formatoTelefono],
  },
  atencion: {
    mascota: [seleccionObligatoria("una mascota")],
    veterinario: [seleccionObligatoria("un veterinario")],
    fecha: [requerido("La fecha es obligatoria."), fechaNoFutura("La fecha de atención")],
    motivo: [requerido("El motivo es obligatorio."), largoMinimo(5, "El motivo")],
    costo_neto: [requerido("El costo es obligatorio."), rangoNumerico(0, 5000000, "El costo")],
  },
};

// ---------- Motor: aplica las reglas y pinta los mensajes ----------

function mostrarError(campo, mensaje) {
  const hueco = campo.form.querySelector(`[data-error-de="${campo.name}"]`);
  if (hueco) hueco.textContent = mensaje || "";
  campo.classList.toggle("invalido", Boolean(mensaje));
}

function validarCampo(campo, validadores) {
  for (const validar of validadores) {
    const mensaje = validar(campo.value);
    if (mensaje) {
      mostrarError(campo, mensaje);
      return false;
    }
  }
  mostrarError(campo, "");
  return true;
}

function conectar(formulario) {
  const reglas = REGLAS[formulario.dataset.validar];
  if (!reglas) return;

  for (const [nombre, validadores] of Object.entries(reglas)) {
    const campo = formulario.elements[nombre];
    if (!campo) continue;
    // Revalidar al salir del campo y al corregir un campo ya marcado.
    campo.addEventListener("blur", () => validarCampo(campo, validadores));
    campo.addEventListener("input", () => {
      if (campo.classList.contains("invalido")) validarCampo(campo, validadores);
    });
  }

  formulario.addEventListener("submit", (evento) => {
    let valido = true;
    let primerFallo = null;

    for (const [nombre, validadores] of Object.entries(reglas)) {
      const campo = formulario.elements[nombre];
      if (!campo) continue;
      if (!validarCampo(campo, validadores)) {
        valido = false;
        primerFallo = primerFallo || campo;
      }
    }

    if (!valido) {
      evento.preventDefault(); // bloquea el envio
      primerFallo.focus();
    }
  });
}

// ---------- Estado "cargando" del listado filtrable ----------

function conectarCargando() {
  const filtros = document.getElementById("form-filtros");
  const cargando = document.getElementById("cargando");
  if (!filtros || !cargando) return;

  filtros.addEventListener("submit", () => {
    document.querySelectorAll(".tabla, .estado").forEach((el) => (el.hidden = true));
    cargando.hidden = false;
  });
}

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("form[data-validar]").forEach(conectar);
  conectarCargando();
});
