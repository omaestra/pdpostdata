# coding=utf-8
from django import forms
from django.forms.widgets import TextInput

from accounts.models import UserProfile

from django.contrib.auth.models import User

from .models import UserAddress

default_errors = {
    'required': 'Este campo es obligatorio!',
    'invalid': 'Por favor, ingresa un valor valido!',
    'min-length': '',
}


class UserForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['class'] = 'form-control'
        self.fields['last_name'].widget.attrs['class'] = 'form-control'

    class Meta:
        model = User
        fields = ['first_name', 'last_name', ]


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['avatar', ]


class PhoneInput(TextInput):
    input_type = 'tel'


class UserAddressForm(forms.ModelForm):
    phone_number = forms.RegexField(regex=r'^\+?1?\d{9,15}$',
                                    label="Telefono",
                                    error_message=("Phone number must be entered in the "
                                                   "format: '+999999999'. Up to 15 digits "
                                                   "allowed."))
    default = forms.BooleanField(label='Direccion por defecto?', required=False)

    class Meta:
        model = UserAddress
        fields = ["address",
                  "address2",
                  "city",
                  "state",
                  "country",
                  "zipcode",
                  ]
        labels = {
            'address': 'Direccion',
            'address2': 'Direccion 2',
            'city': 'Ciudad',
            'state': 'Estado',
            'country': 'Pais',
            'zipcode': 'Codigo Postal',
        }
        help_texts = {
            'address': 'Ej.: Urbanizacion o residencia, Calle, Nro. Apartamento, Piso.',
        }
        error_messages = {
            'address': {
                'max_length': "La direccion es muy larga.",
                'required': "Este campo es necesario.",
            },
            'city': {
                'required': "Este campo es necesario.",
            },
            'country': {
                'required': "Este campo es necesario.",
            },
            'zipcode': {
                'required': "Este campo es necesario.",
            },
            'phone_number': {
                'required': "Este campo es necesario.",
            },
        }

    def __init__(self, *args, **kwargs):
        super(UserAddressForm, self).__init__(*args, **kwargs)
        self.fields['address'].widget.attrs['class'] = 'form-control'
        self.fields['address2'].widget.attrs['class'] = 'form-control'
        self.fields['city'].widget.attrs['class'] = 'form-control'
        self.fields['state'].widget.attrs['class'] = 'form-control'
        self.fields['country'].widget.attrs['class'] = 'form-control'
        self.fields['zipcode'].widget.attrs['class'] = 'form-control'
        self.fields['phone_number'].widget.attrs['class'] = 'form-control'
        self.fields['phone_number'].widget = PhoneInput()


class LoginForm(forms.Form):
    username = forms.CharField(
        error_messages=default_errors,
        widget=forms.TextInput(
            attrs={'id': 'login-username', 'class': 'form-control', 'required': True,
                   'placeholder': 'usuario o correo electronico', 'autofocus': True, }
        )
    )
    password = forms.CharField(
        error_messages=default_errors,
        widget=forms.PasswordInput(
            attrs={'id': 'login-password', 'class': 'form-control', 'required': True, 'placeholder': 'contraseña', }
        )
    )

    def clean_username(self):
        username = self.cleaned_data.get("username")
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise forms.ValidationError("Oops! No podemos encontrar a este usuario.")
        return username

    def clean_password(self):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")
        try:
            user = User.objects.get(username=username)
        except:
            user = None
        if user is not None and not user.check_password(password):
            raise forms.ValidationError("Contraseña invalida!")
        elif user is None:
            pass
        else:
            return password


class RegistrationForm(forms.ModelForm):
    # email = forms.EmailField(label='Your Email')
    password1 = forms.CharField(
        min_length=8,
        label='Password',
        error_messages=default_errors,
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Contraseña','name': 'password1', }
        )
    )
    password2 = forms.CharField(
        min_length=8,
        label='Password Confirmation',
        error_messages=default_errors,
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Confirmar contraseña',
                   'name': 'password2', }
        )
    )

    class Meta:
        model = User
        fields = ['username', 'email', ]

        widgets = {
            'username': forms.TextInput(
                attrs={'id': 'login-username', 'class': 'form-control', 'required': True,
                       'placeholder': 'Nombre de usuario', 'autofocus': True, 'name': 'username', }
            ),
            'email': forms.EmailInput(
                attrs={'class': 'form-control', 'required': True, 'placeholder': 'Correo electronico',
                       'name': 'email', }
            ),
        }

        error_messages = {
            'username': {
                'required': "Este campo es obligatorio!",
            },
            'password': {
                'required': "Este campo es obligatorio!",
            },
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden!")
        return password2

    def clean_email(self):
        email = self.cleaned_data.get("email")
        user_count = User.objects.filter(email=email).count()
        if user_count > 0:
            raise forms.ValidationError(
                "Este correo electronico ya existe! Por favor, "
                "confirma tus datos o reinicia tu contraseña")
        return email

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user
