# tests/test_projects.py
import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from projects.models import Project

User = get_user_model()  # Pobieranie niestandardowego modelu użytkownika


@pytest.mark.django_db
def test_project_list_view_superuser(client):
    # Tworzenie superusera zgodnie z niestandardowym modelem
    admin = User.objects.create_superuser(
        email='admin@example.com',
        password='adminpass123',
        first_name='Admin',
        last_name='User'
    )

    Project.objects.create(name="Project 1", client=admin)
    Project.objects.create(name="Project 2", client=admin)

    client.force_login(admin)
    response = client.get('/projects/')

    assert response.status_code == 200
    assert len(response.context['projects']) == 2


@pytest.mark.django_db
def test_project_list_view_lab_member(client):
    # Tworzenie użytkownika z grupą Lab_member
    group = Group.objects.create(name='Lab_member')
    user = User.objects.create_user(
        email='member@example.com',
        password='memberpass123',
        first_name='Lab',
        last_name='Member',
        user_type='personal'
    )
    user.groups.add(group)

    # Tworzenie klienta-firmy
    company_user = User.objects.create_user(
        email='company@example.com',
        password='companypass123',
        user_type='company',
        company_name='Test Company',
        tax_id='1234567890'
    )

    # Tworzenie projektu z przypisanym klientem i lab memberem
    Project.objects.create(
        name="Assigned Project",
        client=company_user,
        assign_to=user
    )

    client.force_login(user)
    response = client.get('/projects/')

    assert response.status_code == 200
    assert len(response.context['projects']) == 1


@pytest.mark.django_db
def test_project_detail_view_access(client):
    owner = User.objects.create_user(
        email='owner@example.com',
        password='test123',
        user_type='company',
        company_name='Owner Company'
    )
    project = Project.objects.create(name="Test Project", client=owner)

    client.force_login(owner)
    response = client.get(f'/projects/{project.id}/')

    assert response.status_code == 200
    assert response.context['can_edit'] is True


@pytest.mark.django_db
def test_project_delete_view_permission(client):
    user = User.objects.create_user(
        email='deleter@example.com',
        password='test123',
        user_type='personal'
    )

    content_type = ContentType.objects.get_for_model(Project)
    permission = Permission.objects.get(codename='delete_project')
    user.user_permissions.add(permission)

    company = User.objects.create_user(
        email='company@example.com',
        password='test123',
        user_type='company'
    )
    project = Project.objects.create(name="Project to Delete", client=company)

    client.force_login(user)
    response = client.post(f'/projects/{project.id}/delete/')

    assert response.status_code == 302
    assert not Project.objects.filter(id=project.id).exists()