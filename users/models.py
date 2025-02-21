from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .validators import validate_nip

# Create your models here.

class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Użytkownik musi mieć adres email.")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser musi mieć is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser musi mieć is_superuser=True.")
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name','last_name']
    USER_TYPE_CHOICES = [
        ('personal', 'Personal'),
        ('company', 'Company')
    ]
    user_type = models.CharField(max_length=8, choices=USER_TYPE_CHOICES, default='personal')
    company_name = models.CharField(max_length=255, blank=True, null=True)
    company_address = models.CharField(max_length=255, blank=True, null=True)
    tax_id = models.CharField(max_length=10, blank=True, null=True, validators=[validate_nip], verbose_name="NIP")

    objects = UserManager()

    def clean(self):
        super().clean()
        if self.user_type == 'company':
            if not self.company_name or not self.company_address or not self.tax_id:
                raise ValidationError(_("Pola nazwa firmy, adres firmy i NIP są wymagane."))

    def __str__(self):
        return self.email

