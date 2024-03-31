import pytest

from rest_framework.exceptions import ValidationError
from rest_framework.request import Request

from companies.services import QueryParamsValidatorService


def test_valid_date_params(mock_request: Request, material_date_query_params: dict[str, str]):
    mock_request.query_params = material_date_query_params
    assert QueryParamsValidatorService(mock_request)() is True


def test_invalid_date_params(mock_request: Request, invalide_material_date_query_params: dict[str, str]):
    mock_request.query_params = invalide_material_date_query_params
    with pytest.raises(ValidationError):
        QueryParamsValidatorService(mock_request)()
