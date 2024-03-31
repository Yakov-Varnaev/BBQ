import pytest

from pytest_mock import MockerFixture
from rest_framework.request import Request

from app.testing import ApiClient
from users.models import User


@pytest.fixture
def as_anon() -> ApiClient:
    return ApiClient()


@pytest.fixture
def as_user(user: User) -> ApiClient:
    return ApiClient(user=user)


@pytest.fixture
def as_superuser(superuser: User) -> ApiClient:
    return ApiClient(user=superuser)


@pytest.fixture
def mock_request(mocker: MockerFixture) -> Request:
    return mocker.MagicMock(spec=Request)
