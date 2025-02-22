import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def validate_code_name(value):
    if not re.match(r'^[A-Za-z0-9\-]+$', value):
        raise ValidationError(
            _("Nazwa sprawozdania może zawierać litery, cyfry lub -"),
            code="report_code_name_bad_signs",
    )

def validate_material_type(value):
    if not re.match(r'^[A-Z]{3}$', value):
        raise ValidationError(
            _("Typ materiału to 3 duże litery."),
            code="material_type_bad_signs",
        )

def validate_dates(start_date, end_date):
    if start_date and end_date and end_date < start_date:
        raise ValidationError(
            _("Data rozpoczęcia przed datą zakończenia"),
            code="dates_rules",
        )
