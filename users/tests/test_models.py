import pytest
from django.core.exceptions import ValidationError
from users.models import User


# Create your tests here.

@pytest.mark.django_db
def test_create_user():
    user = User.objects.create_user(
        email="test@hogwart.com",
        first_name="Harry",
        last_name="Potter",
        password="password123",
        user_type="personal"
    )
    assert user.email == "test@hogwart.com"
    assert user.check_password("password123")
    assert user.user_type == "personal"
    assert user.company_name is None

@pytest.mark.django_db
def test_create_company_user():
    user = User.objects.create_user(
        email="company@hogwart.com",
        first_name="Harry",
        last_name="Inc",
        password="password123",
        user_type="company",
        company_name="Test Comp",
        company_address="Test Street",
        tax_id="1234567890"
    )
    assert user.user_type == "company"
    assert user.company_name == "Test Comp"

@pytest.mark.django_db
def test_company_user_validation():
    user = User(
        email="invalid@example.com",
        first_name="Test",
        last_name="User",
        user_type="company",
        password="password123"
    )
    with pytest.raises(ValidationError):
        user.full_clean()


