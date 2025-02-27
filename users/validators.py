import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_nip(tax_id):
    nip_digits = re.sub(r'\D', '', tax_id)
    if len(nip_digits) != 10:
        raise ValidationError(_("NIP musi zawierać 10 cyfr."))
    weights = [6, 5, 7, 2, 3, 4, 5, 6, 7]
    try:
        sum_products = sum(
            int(digit) * weight
            for digit, weight in
            zip(nip_digits[:9], weights)
        )
    except ValueError:
        raise ValidationError(_("NIP zawiera nieprawidłowe znaki."))
    control = sum_products % 11
    if control == 10 or control != int(nip_digits[9]):
        raise ValidationError(_("Niepoprawny numer NIP."))


def validate_first_name(first_name):
    if not first_name.isalpha():
        raise ValidationError(
            _("Imię może zawierać tylko litery"),
            code="first_name_with_bad_signs",
        )


def validate_last_name(last_name):
    if not last_name.isalpha():
        raise ValidationError(
            _("Nazwisko może zawierać tylko litery"),
            code="last_name_with_bad_signs",
        )


def validate_exist_email(email):
    from .models import User  # fix cycle import validator -> user
    if User.objects.filter(email=email).exists():
        raise ValidationError(
            _("Email: %(value)s jest już użyty"),
            code="email_exist",
            params={"value": email},
        )


def validate_password_length(password):
    if len(password) < 9:
        raise ValidationError("Hasło to co najmniej 9 znaki")


def validate_password_small_sign(password):
    if not re.search("[a-z]", password):
        raise ValidationError(
            "Hasło musi zawierać co najmniej jedną małą literę."
        )


def validate_password_big_sign(password):
    if not re.search("[A-Z]", password):
        raise ValidationError(
            "Hasło musi zawierać co najmniej jedną wielką literę."
        )


def validate_password_number(password):
    if not re.search("[0-9]", password):
        raise ValidationError("Hasło musi zawierać co najmniej jedną cyfrę.")


def validate_password_space(password):
    if re.search(r"\s", password):
        raise ValidationError("Hasło nie może zawierać spacji.")


def validate_confirm_passwords(password, confirm_password):
    if password != confirm_password:
        raise ValidationError(
            _("Hasła nie są takie same. Z validate_confirm_passwords")
        )
