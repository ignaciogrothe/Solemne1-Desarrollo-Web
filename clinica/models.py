from datetime import date
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


IVA = Decimal("0.19")


def validar_rut(valor):
    """Valida un RUT chileno calculando su digito verificador (modulo 11)."""
    limpio = valor.replace(".", "").replace("-", "").upper()
    if len(limpio) < 2 or not limpio[:-1].isdigit():
        raise ValidationError("El RUT debe tener el formato 12345678-9.")
    cuerpo, digito = limpio[:-1], limpio[-1]
    suma, factor = 0, 2
    for c in reversed(cuerpo):
        suma += int(c) * factor
        factor = 2 if factor == 7 else factor + 1
    resto = 11 - (suma % 11)
    esperado = {11: "0", 10: "K"}.get(resto, str(resto))
    if digito != esperado:
        raise ValidationError("El digito verificador del RUT no es correcto.")


class Especie(models.Model):
    """Especie animal atendida por la clinica (Canino, Felino, etc.)."""

    nombre = models.CharField(max_length=50, unique=True)
    nombre_cientifico = models.CharField(max_length=100, blank=True)
    cuidados_generales = models.TextField(blank=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name = "especie"
        verbose_name_plural = "especies"

    def __str__(self):
        return self.nombre


class Dueno(models.Model):
    """Persona responsable de una o mas mascotas."""

    rut = models.CharField(
        max_length=12,
        unique=True,
        validators=[validar_rut],
        help_text="Formato 12345678-9",
    )
    nombre = models.CharField(max_length=60)
    apellido = models.CharField(max_length=60)
    email = models.EmailField()
    telefono = models.CharField(max_length=15)
    direccion = models.CharField(max_length=150, blank=True)
    fecha_registro = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ["apellido", "nombre"]
        verbose_name = "dueño"
        verbose_name_plural = "dueños"

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.rut})"

    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"

    def cantidad_mascotas(self):
        return self.mascotas.count()


class Veterinario(models.Model):
    """Profesional que realiza las atenciones."""

    nombre = models.CharField(max_length=60)
    apellido = models.CharField(max_length=60)
    email = models.EmailField(unique=True)
    especialidad = models.CharField(max_length=80)
    # Segunda relacion exigida (M:N): un veterinario atiende varias especies
    # y una especie es atendida por varios veterinarios.
    especies_atendidas = models.ManyToManyField(
        Especie,
        related_name="veterinarios",
        blank=True,
    )
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["apellido", "nombre"]
        verbose_name = "veterinario"
        verbose_name_plural = "veterinarios"

    def __str__(self):
        return f"Dr(a). {self.nombre} {self.apellido}"

    def atiende(self, especie):
        """Regla de negocio: solo puede atender especies de su competencia."""
        return self.especies_atendidas.filter(pk=especie.pk).exists()


class MascotaQuerySet(models.QuerySet):
    """Filtros del dominio, reutilizables desde cualquier vista."""

    def activas(self):
        return self.filter(activa=True)

    def filtrar(self, especie_id=None, dueno_id=None, texto=None):
        qs = self
        if especie_id:
            qs = qs.filter(especie_id=especie_id)
        if dueno_id:
            qs = qs.filter(dueno_id=dueno_id)
        if texto:
            qs = qs.filter(nombre__icontains=texto)
        return qs


class Mascota(models.Model):
    """Entidad principal del sistema: el paciente de la clinica."""

    SEXOS = [("M", "Macho"), ("H", "Hembra")]

    nombre = models.CharField(max_length=60)
    # CASCADE: una mascota no existe sin su dueño. Si se borra la ficha del
    # dueño se borra tambien la de sus mascotas, no queda huerfana.
    dueno = models.ForeignKey(
        Dueno,
        on_delete=models.CASCADE,
        related_name="mascotas",
        verbose_name="dueño",
    )
    # PROTECT: la especie es un catalogo. Borrarla arrastraria fichas clinicas
    # historicas, asi que Django impide borrar una especie con mascotas.
    especie = models.ForeignKey(
        Especie,
        on_delete=models.PROTECT,
        related_name="mascotas",
    )
    sexo = models.CharField(max_length=1, choices=SEXOS)
    fecha_nacimiento = models.DateField()
    peso_kg = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.1")), MaxValueValidator(Decimal("200"))],
        verbose_name="peso (kg)",
    )
    activa = models.BooleanField(default=True)

    objects = MascotaQuerySet.as_manager()

    class Meta:
        ordering = ["nombre"]
        verbose_name = "mascota"
        verbose_name_plural = "mascotas"

    def __str__(self):
        return f"{self.nombre} - {self.especie}"

    def clean(self):
        if self.fecha_nacimiento and self.fecha_nacimiento > date.today():
            raise ValidationError(
                {"fecha_nacimiento": "La fecha de nacimiento no puede ser futura."}
            )

    def edad_anios(self):
        """Regla del dominio: existiria igual sin navegador, por eso va aqui."""
        hoy = date.today()
        nacimiento = self.fecha_nacimiento
        return (
            hoy.year
            - nacimiento.year
            - ((hoy.month, hoy.day) < (nacimiento.month, nacimiento.day))
        )

    def es_cachorro(self):
        return self.edad_anios() < 1

    def ultima_atencion(self):
        return self.atenciones.first()


class Atencion(models.Model):
    """Consulta veterinaria: relaciona una mascota con un veterinario."""

    PENDIENTE, REALIZADA, ANULADA = "PEN", "REA", "ANU"
    ESTADOS = [
        (PENDIENTE, "Pendiente"),
        (REALIZADA, "Realizada"),
        (ANULADA, "Anulada"),
    ]

    # CASCADE: la atencion es parte de la ficha clinica de la mascota. Si la
    # mascota deja de existir, su historial tampoco tiene sentido por separado.
    mascota = models.ForeignKey(
        Mascota,
        on_delete=models.CASCADE,
        related_name="atenciones",
    )
    # PROTECT: el historial clinico es evidencia legal. No se puede borrar un
    # veterinario y dejar atenciones sin responsable identificado.
    veterinario = models.ForeignKey(
        Veterinario,
        on_delete=models.PROTECT,
        related_name="atenciones",
    )
    fecha = models.DateField()
    motivo = models.CharField(max_length=150)
    diagnostico = models.TextField(blank=True)
    costo_neto = models.DecimalField(
        max_digits=9,
        decimal_places=0,
        validators=[MinValueValidator(0)],
        verbose_name="costo neto ($)",
    )
    estado = models.CharField(max_length=3, choices=ESTADOS, default=PENDIENTE)

    class Meta:
        ordering = ["-fecha", "-id"]
        verbose_name = "atención"
        verbose_name_plural = "atenciones"

    def __str__(self):
        return f"{self.fecha} · {self.mascota.nombre} · {self.motivo}"

    def clean(self):
        if self.fecha and self.mascota_id:
            if self.fecha < self.mascota.fecha_nacimiento:
                raise ValidationError(
                    {"fecha": "La atención no puede ser anterior al nacimiento de la mascota."}
                )
        if self.veterinario_id and self.mascota_id:
            if not self.veterinario.atiende(self.mascota.especie):
                raise ValidationError(
                    {
                        "veterinario": f"{self.veterinario} no atiende "
                        f"{self.mascota.especie}."
                    }
                )

    def costo_con_iva(self):
        return (self.costo_neto * (1 + IVA)).quantize(Decimal("1"))

    def es_anulable(self):
        return self.estado == self.PENDIENTE
