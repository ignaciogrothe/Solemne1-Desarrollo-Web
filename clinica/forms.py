from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import Mascota


class LoginForm(AuthenticationForm):
    """Login propio: mismo backend de Django, pero con el estilo del sitio."""

    username = forms.CharField(
        label="Usuario",
        widget=forms.TextInput(attrs={"class": "campo", "autofocus": True}),
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={"class": "campo"}),
    )


class MascotaForm(forms.ModelForm):
    class Meta:
        model = Mascota
        fields = ["nombre", "dueno", "especie", "sexo", "fecha_nacimiento", "peso_kg", "activa"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "campo"}),
            # Los <select> se pueblan solos desde la base de datos: Django
            # construye las opciones a partir del queryset de cada FK.
            "dueno": forms.Select(attrs={"class": "campo"}),
            "especie": forms.Select(attrs={"class": "campo"}),
            "sexo": forms.Select(attrs={"class": "campo"}),
            "fecha_nacimiento": forms.DateInput(attrs={"class": "campo", "type": "date"}),
            "peso_kg": forms.NumberInput(attrs={"class": "campo", "step": "0.01"}),
            "activa": forms.CheckboxInput(attrs={"class": "campo-check"}),
        }
