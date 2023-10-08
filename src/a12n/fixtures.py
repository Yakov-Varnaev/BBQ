import pytest

from a12n.factory import RegistrationData, UserData
from app.testing.factory import FixtureFactory


@pytest.fixture
def registration_data(factory: FixtureFactory) -> RegistrationData:
    return factory.registration_data()


@pytest.fixture
def expected_user_data(factory: FixtureFactory, registration_data: RegistrationData) -> UserData:
    return factory.expected_user_data(registration_data)
