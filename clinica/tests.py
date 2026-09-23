"""Pruebas de las reglas de negocio y del control de acceso.

Ejecutar con:  python manage.py test clinica
"""

from datetime import date
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from .models import Atencion, Dueno, Especie, Mascota, Veterinario, validar_rut


class ReglasDelModeloTest(TestCase):
    def setUp(self):
        self.felino = Especie.objects.create(nombre="Felino")
        self.conejo = Especie.objects.create(nombre="Conejo")
        self.dueno = Dueno.objects.create(
            rut="12345678-5", nombre="María", apellido="González",
            email="m@correo.cl", telefono="+56912345678",
        )
        self.gata = Mascota.objects.create(
            nombre="Luna", dueno=self.dueno, especie=self.felino, sexo="H",
            fecha_nacimiento=date(2021, 7, 2), peso_kg=Decimal("4.20"),
        )
        self.vet_felinos = Veterinario.objects.create(
            nombre="Andrés", apellido="Fuentes",
            email="a@patitas.cl", especialidad="Medicina interna",
        )
        self.vet_felinos.especies_atendidas.add(self.felino)
        self.vet_exoticos = Veterinario.objects.create(
            nombre="Ignacio", apellido="Cárdenas",
            email="i@patitas.cl", especialidad="Exóticos",
        )
        self.vet_exoticos.especies_atendidas.add(self.conejo)

    def test_rut_valido_pasa_y_rut_invalido_falla(self):
        validar_rut("12345678-5")  # no debe lanzar
        with self.assertRaises(ValidationError):
            validar_rut("12345678-9")

    def test_edad_se_calcula_desde_la_fecha_de_nacimiento(self):
        esperada = date.today().year - 2021 - (
            (date.today().month, date.today().day) < (7, 2)
        )
        self.assertEqual(self.gata.edad_anios(), esperada)

    def test_no_se_acepta_mascota_nacida_en_el_futuro(self):
        futura = Mascota(
            nombre="Fantasma", dueno=self.dueno, especie=self.felino, sexo="M",
            fecha_nacimiento=date(date.today().year + 1, 1, 1), peso_kg=Decimal("3"),
        )
        with self.assertRaises(ValidationError):
            futura.full_clean()

    def test_costo_con_iva_aplica_el_19_por_ciento(self):
        atencion = Atencion(
            mascota=self.gata, veterinario=self.vet_felinos,
            fecha=date.today(), motivo="Control", costo_neto=Decimal("30000"),
        )
        self.assertEqual(atencion.costo_con_iva(), Decimal("35700"))

    def test_veterinario_no_puede_atender_especie_ajena(self):
        atencion = Atencion(
            mascota=self.gata, veterinario=self.vet_exoticos,
            fecha=date.today(), motivo="Control", costo_neto=Decimal("30000"),
        )
        with self.assertRaises(ValidationError):
            atencion.full_clean()

    def test_atencion_no_puede_ser_anterior_al_nacimiento(self):
        atencion = Atencion(
            mascota=self.gata, veterinario=self.vet_felinos,
            fecha=date(2019, 1, 1), motivo="Control", costo_neto=Decimal("10000"),
        )
        with self.assertRaises(ValidationError):
            atencion.full_clean()

    def test_borrar_especie_con_mascotas_esta_protegido(self):
        from django.db.models import ProtectedError

        with self.assertRaises(ProtectedError):
            self.felino.delete()

    def test_borrar_dueno_arrastra_a_sus_mascotas(self):
        self.dueno.delete()
        self.assertEqual(Mascota.objects.count(), 0)


class ControlDeAccesoTest(TestCase):
    def test_vista_de_gestion_redirige_al_login_sin_sesion(self):
        respuesta = self.client.get(reverse("clinica:mascota_lista"))
        self.assertRedirects(
            respuesta,
            f"{reverse('clinica:login')}?next={reverse('clinica:mascota_lista')}",
        )

    def test_con_sesion_la_vista_responde(self):
        User.objects.create_user("recepcion", password="Recepcion2026!")
        self.client.login(username="recepcion", password="Recepcion2026!")
        respuesta = self.client.get(reverse("clinica:mascota_lista"))
        self.assertEqual(respuesta.status_code, 200)


class EstadoDeErrorTest(TestCase):
    """Si la base falla, el listado muestra el estado de error, no un 500."""

    def test_el_listado_avisa_en_vez_de_caerse(self):
        from unittest.mock import patch

        from django.db import DatabaseError

        User.objects.create_user("recepcion", password="Recepcion2026!")
        self.client.login(username="recepcion", password="Recepcion2026!")

        with patch.object(Especie.objects, "all", side_effect=DatabaseError("caida")):
            respuesta = self.client.get(reverse("clinica:mascota_lista"))

        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "No se pudo consultar la base de datos")
