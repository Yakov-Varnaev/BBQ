import pytest

from rest_framework.exceptions import ValidationError

from django.http.request import QueryDict

from companies.services import DateValidatorService


def test_valid_date_params(material_date_query_params: dict[str, str]):
    query_params = QueryDict(mutable=True)
    query_params.update(**material_date_query_params)

    assert DateValidatorService(query_params)() is True


def test_only_date_from_param(material_date_query_params: dict[str, str]):
    del material_date_query_params["date_to"]
    query_params = QueryDict(mutable=True)
    query_params.update(**material_date_query_params)

    assert DateValidatorService(query_params)() is True


def test_only_date_to_param(material_date_query_params: dict[str, str]):
    del material_date_query_params["date_from"]
    query_params = QueryDict(mutable=True)
    query_params.update(**material_date_query_params)

    assert DateValidatorService(query_params)() is True


def test_invalid_date_params(invalide_material_date_query_params: dict[str, str]):
    query_params = QueryDict(mutable=True)
    query_params.update(**invalide_material_date_query_params)

    with pytest.raises(ValidationError):
        DateValidatorService(query_params)()
