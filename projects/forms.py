from django import forms
from django.db.models import Q

from .models import Project, Sample, Report
from users.models import User


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'client', 'assign_to', 'status']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)


class SampleForm(forms.ModelForm):
    class Meta:
        model = Sample
        fields = ['name', 'description', 'material_type', 'collection_date']
        widgets = {
            'collection_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['code_name', 'project', 'sample', 'start_date', 'end_date', 'research_standards']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

        self.fields['project'].queryset = Project.objects.all()

        self.fields['sample'].queryset = Sample.objects.filter(
            Q(report__isnull=True) | Q(report__id=self.instance.pk)
        )