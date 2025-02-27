from django import forms
from .models import Project, Sample, Report
from users.models import User


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'client', 'assign_to', 'status']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

        if user.user_type == 'company':
            self.fields['client'].queryset = User.objects.filter(pk=user.pk)
            self.fields['client'].initial = user
            self.fields['client'].disabled = True
        else:
            self.fields['client'].queryset = User.objects.filter(user_type='company')
            self.fields['assign_to'].queryset = User.objects.filter(groups__name='Lab_member')


class SampleForm(forms.ModelForm):
    class Meta:
        model = Sample
        fields = ['name', 'description', 'material_type', 'collection_date']
        widgets = {
            'collection_date': forms.DateInput(attrs={'type': 'date'}),
        }


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

        if user.user_type == 'company':
            self.fields['project'].queryset = Project.objects.filter(client=user)
        else:
            self.fields['project'].queryset = Project.objects.all()

        self.fields['sample'].queryset = Sample.objects.none()
        if 'project' in self.data:
            try:
                project_id = int(self.data.get('project'))
                self.fields['sample'].queryset = Sample.objects.filter(report__isnull=True, project=project_id)
            except (ValueError, TypeError):
                pass