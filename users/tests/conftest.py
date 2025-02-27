import pytest
from users.models import User


@pytest.fixture
def user():
    return User.objects.create_user(
        email="test@hogwart.com",
        first_name="Harry",
        last_name="Potter",
        password="Password123!"
    )

@pytest.fixture
def authenticated_user(client, user):
    client.login(email=user.email, password="password123!")
    return user