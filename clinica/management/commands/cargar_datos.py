"""Carga los datos de prueba de la clinica: python manage.py cargar_datos"""

from datetime import date
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from clinica.models import Atencion, Dueno, Especie, Mascota, Veterinario


ESPECIES = [
    ("Canino", "Canis lupus familiaris", "Vacuna séxtuple anual y desparasitación cada 3 meses."),
    ("Felino", "Felis catus", "Vacuna triple felina anual. Control de pulgas mensual."),
    ("Conejo", "Oryctolagus cuniculus", "Dieta alta en fibra. Control dental semestral."),
    ("Ave", "Serinus canaria", "Evitar corrientes de aire. Control de plumaje."),
]

DUENOS = [
    ("12345678-5", "María", "González", "maria.gonzalez@correo.cl", "+56912345678", "Av. Los Leones 1245, Providencia"),
    ("9876543-3", "Pedro", "Ramírez", "pramirez@correo.cl", "+56987654321", "Calle Serrano 480, Valparaíso"),
    ("15678234-3", "Camila", "Soto", "camila.soto@correo.cl", "+56955512340", "Pasaje Los Robles 78, Maipú"),
    ("17456789-5", "Jorge", "Muñoz", "jmunoz@correo.cl", "+56944498211", "Av. Alemania 3390, Temuco"),
    ("11222333-8", "Valentina", "Rojas", "vrojas@correo.cl", "+56966677889", "El Vergel 220, Ñuñoa"),
]

VETERINARIOS = [
    ("Andrés", "Fuentes", "afuentes@patitas.cl", "Medicina interna de pequeños animales", ["Canino", "Felino"]),
    ("Paula", "Bravo", "pbravo@patitas.cl", "Cirugía y traumatología", ["Canino", "Felino", "Conejo"]),
    ("Ignacio", "Cárdenas", "icardenas@patitas.cl", "Animales exóticos", ["Conejo", "Ave"]),
]

MASCOTAS = [
    ("Rocky", "12345678-5", "Canino", "M", date(2019, 3, 14), "28.50"),
    ("Luna", "12345678-5", "Felino", "H", date(2021, 7, 2), "4.20"),
    ("Simón", "9876543-3", "Canino", "M", date(2016, 11, 25), "12.80"),
    ("Pelusa", "9876543-3", "Conejo", "H", date(2023, 1, 9), "1.90"),
    ("Trufa", "15678234-3", "Felino", "H", date(2020, 5, 30), "3.85"),
    ("Bruno", "15678234-3", "Canino", "M", date(2022, 9, 18), "19.40"),
    ("Kiwi", "17456789-5", "Ave", "M", date(2024, 2, 11), "0.35"),
    ("Nala", "17456789-5", "Canino", "H", date(2018, 6, 6), "24.10"),
    ("Michi", "11222333-8", "Felino", "M", date(2023, 12, 1), "3.10"),
    ("Copito", "11222333-8", "Conejo", "M", date(2022, 4, 22), "2.35"),
]

ATENCIONES = [
    ("Rocky", "afuentes@patitas.cl", date(2026, 3, 4), "Control anual y vacuna séxtuple",
     "Paciente en buen estado general. Se aplica refuerzo de vacuna.", 28000, Atencion.REALIZADA),
    ("Luna", "afuentes@patitas.cl", date(2026, 4, 17), "Vómitos intermitentes",
     "Gastritis leve. Se indica dieta blanda por 5 días.", 32000, Atencion.REALIZADA),
    ("Simón", "pbravo@patitas.cl", date(2026, 5, 8), "Cojera en pata trasera derecha",
     "Sospecha de luxación rotuliana grado II. Se solicita radiografía.", 45000, Atencion.REALIZADA),
    ("Pelusa", "icardenas@patitas.cl", date(2026, 6, 21), "Control dental",
     "Sobrecrecimiento de incisivos. Se realiza limado.", 38000, Atencion.REALIZADA),
    ("Trufa", "afuentes@patitas.cl", date(2026, 7, 3), "Desparasitación interna",
     "Sin hallazgos. Se administra antiparasitario oral.", 18000, Atencion.REALIZADA),
    ("Bruno", "pbravo@patitas.cl", date(2026, 7, 29), "Herida en almohadilla plantar",
     "Corte superficial. Se limpia y venda.", 25000, Atencion.REALIZADA),
    ("Kiwi", "icardenas@patitas.cl", date(2026, 8, 12), "Pérdida de plumaje",
     "Muda estacional dentro de lo normal. Se ajusta dieta.", 22000, Atencion.REALIZADA),
    ("Nala", "pbravo@patitas.cl", date(2026, 9, 2), "Esterilización programada",
     "", 120000, Atencion.PENDIENTE),
    ("Michi", "afuentes@patitas.cl", date(2026, 9, 10), "Primera consulta y vacuna triple felina",
     "", 30000, Atencion.PENDIENTE),
    ("Copito", "icardenas@patitas.cl", date(2026, 9, 12), "Control de peso",
     "", 15000, Atencion.PENDIENTE),
]


class Command(BaseCommand):
    help = "Carga especies, dueños, veterinarios, mascotas, atenciones y usuarios de prueba."

    @transaction.atomic
    def handle(self, *args, **opciones):
        especies = {
            nombre: Especie.objects.get_or_create(
                nombre=nombre,
                defaults={"nombre_cientifico": cientifico, "cuidados_generales": cuidados},
            )[0]
            for nombre, cientifico, cuidados in ESPECIES
        }

        duenos = {
            rut: Dueno.objects.get_or_create(
                rut=rut,
                defaults={
                    "nombre": nombre,
                    "apellido": apellido,
                    "email": email,
                    "telefono": telefono,
                    "direccion": direccion,
                },
            )[0]
            for rut, nombre, apellido, email, telefono, direccion in DUENOS
        }

        veterinarios = {}
        for nombre, apellido, email, especialidad, sus_especies in VETERINARIOS:
            vet, _ = Veterinario.objects.get_or_create(
                email=email,
                defaults={"nombre": nombre, "apellido": apellido, "especialidad": especialidad},
            )
            vet.especies_atendidas.set([especies[e] for e in sus_especies])
            veterinarios[email] = vet

        mascotas = {}
        for nombre, rut, especie, sexo, nacimiento, peso in MASCOTAS:
            mascota, _ = Mascota.objects.get_or_create(
                nombre=nombre,
                dueno=duenos[rut],
                defaults={
                    "especie": especies[especie],
                    "sexo": sexo,
                    "fecha_nacimiento": nacimiento,
                    "peso_kg": Decimal(peso),
                },
            )
            mascotas[nombre] = mascota

        for nombre, email_vet, fecha, motivo, diagnostico, costo, estado in ATENCIONES:
            Atencion.objects.get_or_create(
                mascota=mascotas[nombre],
                veterinario=veterinarios[email_vet],
                fecha=fecha,
                defaults={
                    "motivo": motivo,
                    "diagnostico": diagnostico,
                    "costo_neto": costo,
                    "estado": estado,
                },
            )

        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@patitas.cl", "Admin2026!")
        if not User.objects.filter(username="recepcion").exists():
            User.objects.create_user("recepcion", "recepcion@patitas.cl", "Recepcion2026!")

        total = (
            Especie.objects.count()
            + Dueno.objects.count()
            + Veterinario.objects.count()
            + Mascota.objects.count()
            + Atencion.objects.count()
        )
        self.stdout.write(self.style.SUCCESS(f"Datos cargados. {total} registros en total."))
