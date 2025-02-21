from django import forms
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from .validators import (
    validate_first_name,
    validate_last_name,
    validate_exist_email,
    validate_password_length,
    validate_password_small_sign,
    validate_password_big_sign,
    validate_password_number,
    validate_password_space,
    validate_confirm_passwords,
)

from .models import User

class RegisterForm(forms.ModelForm):
    first_name = forms.CharField(validators=[validate_first_name])
    last_name = forms.CharField(validators=[validate_last_name])
    email = forms.EmailField(required=True, validators=[validate_exist_email, validate_email])

    password = forms.CharField(
        widget=forms.PasswordInput(),
        label="Hasło",
        validators=[validate_password_length, validate_password_small_sign, validate_password_big_sign,
                    validate_password_number, validate_password_space]
    )
    confirm_password = forms.CharField(
        # widget=forms.PasswordInput(),
        label="Powtórz hasło"
    )

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'user_type', 'company_name', 'company_address', 'tax_id']

    def clean(self):
        cd = super().clean() #Słownik co pobiera dane po przetworzeniu to_python(), validate() i run_validators()
        password = cd.get("password")
        confirm_password = cd.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', 'Hasła muszą być identyczne.')
        return cd

class LoginForm(forms.Form): # nie tworzy i nie zapisuje modelu!
    email = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput, label="Hasło")

    def clean(self):
        cd = super().clean()
        email = cd.get("email")
        password = cd.get("password")

        if email and password:
            user = authenticate(email=email, password=password)
            if user is None:
                raise ValidationError("Wprowadź poprawne dane")
        return cd

