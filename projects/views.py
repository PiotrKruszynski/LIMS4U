from django.http import HttpResponseForbidden
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .models import Project, Sample, Report, ResearchStandard
from .forms import ProjectForm, SampleForm, ReportForm


# Project Views ____________________________________________________________________________________________________

class ProjectListView(LoginRequiredMixin,ListView):
    model = Project
    template_name = 'project_list.html'
    context_object_name = 'projects'
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user

        # Superuser z dostępem do wszystkich projektów
        if user.is_superuser:
            return Project.objects.all()

        # Lab_member z dostępem do przypisanych !brak obsługi oczekujących!
        if user.groups.filter(name='Lab_member').exists():
            return Project.objects.filter(assign_to=user)

        # Lab_user z dostępem do własnych
        if user.groups.filter(name='Lab_user').exists():
            return Project.objects.filter(client=user)

        # Zabezpieczeni w przypadku braku grupy na Użytkowniku
        return Project.objects.none()

class ProjectCreateView(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'project_form.html'
    success_url = reverse_lazy('project_list')
    permission_required = 'projects.add_project'

    # nadpisuje aby przekazać użytkownika do formularza
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    # w przypadku braku uprawnien wyskoczył 403 Forbidden - brak uprawnienia.
    def handle_no_permission(self):
        if self.raise_exception or self.request.user.is_authenticated:
            user_email = self.request.user.email
            requested_url = self.request.path
            return HttpResponseForbidden(f"Otrzymujesz tą wiadomość, ponieważ użytkownik: {user_email} nie ma dostępu do strony:<br> {requested_url} ")
        return super().handle_no_permission()

class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'project_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_edit'] = self.request.user == self.object.client or self.request.user == self.object.assign_to
        return context

class ProjectUpdateView(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'project_form.html'
    success_url = reverse_lazy('project_list')
    permission_required = 'projects.update_project'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def handle_no_permission(self):
        if self.raise_exception or self.request.user.is_authenticated:
            user_email = self.request.user.email
            requested_url = self.request.path
            return HttpResponseForbidden(f"Otrzymujesz tą wiadomość, ponieważ użytkownik: {user_email} nie ma dostępu do strony:<br> {requested_url} ")
        return super().handle_no_permission()

class ProjectDeleteView(PermissionRequiredMixin, LoginRequiredMixin, DeleteView):
    model = Project
    template_name = 'project_confirm_delete.html'
    success_url = reverse_lazy('project_list')
    permission_required = 'projects.delete_project'

    def handle_no_permission(self):
        if self.raise_exception or self.request.user.is_authenticated:
            user_email = self.request.user.email
            requested_url = self.request.path
            return HttpResponseForbidden(f"Otrzymujesz tą wiadomość, ponieważ użytkownik: {user_email} nie ma dostępu do strony:<br> {requested_url} ")
        return super().handle_no_permission()

# Sample Views ____________________________________________________________________________________________________

class SampleListView(LoginRequiredMixin, ListView):
    model = Sample
    template_name = 'sample_list.html'
    paginate_by = 15

    def get_queryset(self):
        return Sample.objects.filter(report__project__client=self.request.user)

class SampleCreateView(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    model = Sample
    form_class = SampleForm
    template_name = 'sample_form.html'
    success_url = reverse_lazy('sample_list')
    permission_required = 'projects.add_sample'

    def handle_no_permission(self):
        if self.raise_exception or self.request.user.is_authenticated:
            user_email = self.request.user.email
            requested_url = self.request.path
            return HttpResponseForbidden(f"Otrzymujesz tą wiadomość, ponieważ użytkownik: {user_email} nie ma dostępu do strony:<br> {requested_url} ")
        return super().handle_no_permission()

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

class SampleDetailView(LoginRequiredMixin, DetailView):
    model = Sample
    template_name = 'sample_detail.html'

# Report Views  ____________________________________________________________________________________________________

class ReportListView(LoginRequiredMixin, ListView):
    model = Report
    template_name = 'report_list.html'

    def get_queryset(self):
        if self.request.user.user_type == 'company':
            return Report.objects.filter(project__client=self.request.user)
        return Report.objects.all()

class ReportCreateView(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    model = Report
    form_class = ReportForm
    template_name = 'report_form.html'
    success_url = reverse_lazy('report_list')
    permission_required = 'projects.add_report'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def handle_no_permission(self):
        if self.raise_exception or self.request.user.is_authenticated:
            user_email = self.request.user.email
            requested_url = self.request.path
            return HttpResponseForbidden(f"Otrzymujesz tą wiadomość, ponieważ użytkownik: {user_email} nie ma dostępu do strony:<br> {requested_url} ")
        return super().handle_no_permission()

class ReportDetailView(LoginRequiredMixin, DetailView):
    model = Report
    template_name = 'report_detail.html'
    slug_field = 'code_name'
    slug_url_kwarg = 'code_name'

# Standard Views  ____________________________________________________________________________________________________

class ResearchStandardListView(LoginRequiredMixin, ListView):
    model = ResearchStandard
    template_name = 'standard_list.html'
    paginate_by = 20