import pytest

from rest_framework.exceptions import ValidationError
from rest_framework.request import Request

from companies.services import DateValidatorService


def test_valid_date_params(mock_request: Request, material_date_query_params: dict[str, str]):
    mock_request.query_params = material_date_query_params

    assert DateValidatorService(mock_request)() is True


def test_only_date_from_param(mock_request: Request, material_date_query_params: dict[str, str]):
    del material_date_query_params["date_to"]
    mock_request.query_params = material_date_query_params

    assert DateValidatorService(mock_request)() is True


def test_only_date_to_param(mock_request: Request, material_date_query_params: dict[str, str]):
    del material_date_query_params["date_from"]
    mock_request.query_params = material_date_query_params

    assert DateValidatorService(mock_request)() is True


def test_invalid_date_params(mock_request: Request, invalide_material_date_query_params: dict[str, str]):
    mock_request.query_params = invalide_material_date_query_params
    with pytest.raises(ValidationError):
        DateValidatorService(mock_request)()
