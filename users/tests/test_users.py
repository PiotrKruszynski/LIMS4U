import pytest
from users.models import User
from users.forms import RegisterForm



# Create your tests here.

@pytest.mark.django_db
def test_register_view_get(client):
    # Test poprawnego URL
    response = client.get("/register/")
    assert response.status_code == 200

    # Test istnienia formularza w kontekście
    assert isinstance(response.context["form"], RegisterForm)

@pytest.mark.django_db
def test_register_view_post_success(client):
    data = {
        "email": "new@hogwart.com",
        "first_name": "Harry",
        "last_name": "Potter",
        "password": "SecurePass123!",
        "confirm_password": "SecurePass123!",
        "user_type": "personal",
    }
    response = client.post("/register/", data)
    assert response.status_code == 302
    assert User.objects.filter(email="new@hogwart.com").exists()


@pytest.mark.django_db
def test_login_view_success(client, user):
    response = client.post("/login/", {
        "email": user.email,
        "password": "Password123!"
    })
    assert response.status_code == 302
    assert response.url == "/projects/"

@pytest.mark.django_db
def test_login_view_invalid_credentials(client, user):
    response = client.post("/login/", {
        "email": user.email,
        "password": "wrong_password"
    })
    assert response.status_code == 200

@pytest.mark.django_db
def test_logout_view(client, authenticated_user):
    client.force_login(authenticated_user)
    response = client.get("/logout/")
    assert response.status_code == 302
    assert response.url == "/login/"

@pytest.mark.django_db
def test_user_profile_view(client, authenticated_user):
    client.force_login(authenticated_user)
    response = client.get("/user/profile/")
    assert response.status_code == 200
