from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from .validators import validate_code_name, validate_material_type, validate_dates

# https://docs.djangoproject.com/en/5.1/topics/auth/customizing/ Instead of referring to User directly, you should reference the user model using django.contrib.auth.get_user_model(). This method will return the currently active user model – the custom user model if one is specified, or User otherwise.
User = get_user_model()

# Project model ______________________________________________________________________________________________________
# powiązanie między Sample a Project idzie przez Report

class Project(models.Model):
    # https://docs.djangoproject.com/en/5.1/ref/models/fields/
    class StatusChoices(models.TextChoices):
        OPEN = 'open', 'Open'
        CLOSED = 'closed', 'Closed'
        AWAITING_APPROVAL = 'awaiting approval', 'Awaiting Approval'

    name = models.CharField("Nazwa projektu", max_length=64)
    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'user_type': 'company'},
        related_name='projects_as_client' # relacja odwrotna dodana z powodu błędu
    )
    assign_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'groups__name': "Lab_member"},
        related_name='projects_as_assignee' # relacja odwrotna dodana z powodu błędu
    )
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.OPEN
    )
    end_date = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = _("Projekt")
        verbose_name_plural = _("Projekty")
        ordering = ['-name']

    def save(self, *args, **kwargs):
        # Zamknięcie projektu -> ustaw datę
        if self.status == self.StatusChoices.CLOSED:
            if not  self.end_date:
                self.end_date = timezone.now().date()
        # Otwarty projekt -> resetuj datę
        elif self.status != self.StatusChoices.CLOSED and self.end_date:
            self.end_date = None

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Projekt: {self.name} | Klient: {self.client.email} | Status: {self.status}"

# Sample model ______________________________________________________________________________________________________

class Sample(models.Model):
    class MaterialType(models.TextChoices):
        UNSELECTED = "UNS", "Unselected"
        CONCRETE = "CON", "Concrete"
        EXTERIOR_FACADE = "EXF", "Exterior Facade"
        SPORTS_SURFACE = "SPS", "Sports Surface"
        PULL_OFF = "OFF", "Pull-off"
        WALLPAPER = "WAP", "Wallpaper"
        SYNTHETIC_TURF = "SYT", "Synthetic Turf"
        PLASTER_AND_ADHESIVES = "PLA", "Plaster and Adhesives"
        CONCRETE_PREFABRICATED = "CPR", "Concrete Prefabricated Products"
        FLOOR_COVERING = "FLC", "Floor Covering"
        SANITARY_PRODUCT = "SAN", "Sanitary Product"
        EXTERIOR_SHUTTERS = "EXS", "Exterior Shutters"

    name = models.CharField("Nazwa próbki", max_length=50)
    description = models.TextField(null=True, blank=True)
    material_type = models.CharField(max_length=3, choices=MaterialType.choices, default=MaterialType.UNSELECTED, validators=[validate_material_type])
    collection_date = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = _("Próbka")
        verbose_name_plural = _("Próbki")
        ordering = ['-collection_date']

    def clean(self):
        if self.collection_date and self.collection_date > timezone.now().date():
            raise ValidationError("Data pobrania próbki nie może być w przyszłości")

    def __str__(self):
        material = self.get_material_type_display() # metoda get_FIELDNAME_display()
        return f"{self.name} ({material if material != 'Unselected' else 'Materiał nie został wybrany'})"

# ResearchStandard model ______________________________________________________________________________________________

class ResearchStandard(models.Model):
    name = models.CharField("Norma badawcza", max_length=50, help_text="Nazwa normy badawczej np. PN-EN 206")
    method = models.CharField(max_length=50, help_text="Metoda badania np. Wytrzymałość na ściskanie")

    class Meta:
        verbose_name = _("Norma Badawcza")
        verbose_name_plural = _("Normy Badawcze")
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'method'],
                name='unique_standard_method'
            )
        ]

    def __str__(self):
        return f"Norma: {self.name} |Metoda badawcza: {self.method}"

# Report model _____________________________________________________________________________________________

class Report(models.Model):
    code_name = models.CharField("Numer sprawozdania", max_length=16, unique=True, validators=[validate_code_name], help_text="Numer sprawozdania (litery/numery/-)")
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    sample = models.OneToOneField(Sample, on_delete=models.SET_NULL, null=True, blank=True, related_name='report')
    research_standards = models.ManyToManyField(ResearchStandard,through='ReportResearchStandard',related_name='reports') # a bez related_name byłoby report_set_all
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'groups__name': "Lab_member"},
        verbose_name="Akceptacja wyników:"
    )

    class Meta:
        verbose_name = _("Sprawozdanie")
        verbose_name_plural = _("Sprawozdania")
        ordering = ['-start_date']

    def clean(self):
        validate_dates(self.start_date, self.end_date)
        if self.sample and self.start_date:
            if self.sample.collection_date > self.start_date:
                raise ValidationError("Sprawozdanie nie może rozpoczynać się przed datą pobrania próbki")

    def __str__(self):
        return f"Sprawozdanie: {self.code_name} | Projekt: {self.project.name}"

# ReportResearchStandard model ______________________________________________________________________________________

class ReportResearchStandard(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    research_standard = models.ForeignKey(ResearchStandard, on_delete=models.CASCADE)
    result = models.CharField(max_length=16, blank=True, null=True)
    evaluation = models.TextField(blank=True, null=True)

    class Meta: # https://docs.djangoproject.com/en/5.1/ref/models/constraints/
        constraints = [ models.UniqueConstraint(fields=['report', 'research_standard'], name='unique_report_standard')]

    def __str__(self):
        return f"Norma: {self.research_standard.name} w sprawozdaniu nr: {self.report.code_name}"