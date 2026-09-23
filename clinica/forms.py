from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import Atencion, Dueno, Mascota


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


class DuenoForm(forms.ModelForm):
    class Meta:
        model = Dueno
        fields = ["rut", "nombre", "apellido", "email", "telefono", "direccion"]
        widgets = {
            "rut": forms.TextInput(attrs={"class": "campo", "placeholder": "12345678-9"}),
            "nombre": forms.TextInput(attrs={"class": "campo"}),
            "apellido": forms.TextInput(attrs={"class": "campo"}),
            "email": forms.EmailInput(attrs={"class": "campo"}),
            "telefono": forms.TextInput(attrs={"class": "campo", "placeholder": "+56912345678"}),
            "direccion": forms.TextInput(attrs={"class": "campo"}),
        }


class AtencionForm(forms.ModelForm):
    """El desplegable dependiente vive aqui: se elige dueño y se filtran sus mascotas."""

    dueno = forms.ModelChoiceField(
        queryset=Dueno.objects.all(),
        label="Dueño",
        widget=forms.Select(attrs={"class": "campo", "id": "id_dueno_filtro"}),
    )

    class Meta:
        model = Atencion
        fields = ["mascota", "veterinario", "fecha", "motivo", "diagnostico", "costo_neto", "estado"]
        widgets = {
            "mascota": forms.Select(attrs={"class": "campo"}),
            "veterinario": forms.Select(attrs={"class": "campo"}),
            "fecha": forms.DateInput(attrs={"class": "campo", "type": "date"}),
            "motivo": forms.TextInput(attrs={"class": "campo"}),
            "diagnostico": forms.Textarea(attrs={"class": "campo", "rows": 3}),
            "costo_neto": forms.NumberInput(attrs={"class": "campo", "step": "1"}),
            "estado": forms.Select(attrs={"class": "campo"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["dueno"].required = False
        if self.instance.pk:
            self.fields["dueno"].initial = self.instance.mascota.dueno_id
