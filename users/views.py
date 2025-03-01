from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import Group
from django.contrib import messages

from .forms import RegisterForm, LoginForm, UserProfileForm


class RegisterView(View):
    def get(self, request):
        form = RegisterForm()
        ctx = {'form': form}
        return render(request, 'register.html', ctx)

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            default_group = Group.objects.get(name='Lab_user')
            user.groups.add(default_group)
            login(request, user)
            messages.success(request, 'Zarejestrowano i zalogowano pomyślnie!')
            return redirect('project_list')
        messages.error(request, 'Popraw błędy w formularzu')
        ctx = {'form': form}
        return render(request, 'register.html', ctx)


class LoginView(View):
    def get(self, request):
        form = LoginForm()
        ctx = {'form': form}
        return render(request, 'login.html', ctx)

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(email=email, password=password)
            if user:
                login(request, user)
                return redirect('project_list')
        return render(request, 'login.html', {'form': form})


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('login')


class UserProfileView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        form = UserProfileForm()
        ctx = {
            'user': user,
            'form': form,
            'is_company': user.user_type == 'company'
        }
        return render(request, 'user_profile.html', ctx)


class UserProfileEditView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        form = UserProfileForm(instance=user)
        context = {
            'form': form,
            'is_company': user.user_type == 'company'
        }
        return render(request, 'user_form.html', context)

    def post(self, request):
        user = request.user
        form = UserProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Konto użytkownika zostało zaktualizowane')
            return redirect('user_profile')
        messages.error(request, 'Wystąpił błąd przy próbie aktualizacji konta')
        context = {
            'form': form,
            'is_company': user.user_type == 'company'
        }
        return render(request, 'user_form.html', context)
