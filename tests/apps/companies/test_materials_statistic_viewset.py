import pytest
from datetime import datetime

from freezegun import freeze_time
from rest_framework import status

from django.urls import reverse
from django.utils import timezone

from app.testing import StatusApiClient
from app.types import RestPageAssertion
from companies.api.serializers import MaterialsStatisticSerializer
from companies.models import Material, Point, StockMaterial
from purchases.models import UsedMaterial

pytestmark = [pytest.mark.django_db]


def test_point_non_managing_staff_cannot_read_materials_statistic(
    as_point_non_managing_staff: StatusApiClient,
    point_with_materials_statistic: Point,
):
    as_point_non_managing_staff.get(  # type: ignore[no-untyped-call]
        reverse(
            "api_v1:companies:materials-statistic-list",
            kwargs={
                "company_pk": point_with_materials_statistic.company.id,
                "point_pk": point_with_materials_statistic.id,
            },
        ),
        expected_status=as_point_non_managing_staff.expected_status,
    )


def test_point_managing_staff_can_read_materials_statistic(
    as_point_managing_staff: StatusApiClient,
    point_with_materials_statistic: Point,
):
    as_point_managing_staff.get(  # type: ignore[no-untyped-call]
        reverse(
            "api_v1:companies:materials-statistic-list",
            kwargs={
                "company_pk": point_with_materials_statistic.company.id,
                "point_pk": point_with_materials_statistic.id,
            },
        ),
    )


@pytest.mark.parametrize(
    "date_query_params",
    [
        {"date_from": "2000-01-01", "date_to": "2222"},
        # {"date_from": "2222-01-01", "date_to": "2002-01-01"},
    ],
)
def test_point_managing_staff_cannot_read_materials_statistic_with_invalid_query_params(
    as_point_managing_staff: StatusApiClient,
    point_with_materials_statistic: Point,
    date_query_params: dict[str, str],
):
    as_point_managing_staff.get(  # type: ignore[no-untyped-call]
        reverse(
            "api_v1:companies:materials-statistic-list",
            kwargs={
                "company_pk": point_with_materials_statistic.company.id,
                "point_pk": point_with_materials_statistic.id,
            },
        ),
        expected_status=status.HTTP_400_BAD_REQUEST,
        data=date_query_params,
    )


def test_materials_statistic_list(
    as_point_managing_staff: StatusApiClient,
    point_with_materials_statistic: Point,
    assert_rest_page: RestPageAssertion,
    material_date_query_params: dict[str, str],
):
    materials_statistic = Material.objects.statistic(point_with_materials_statistic.id, **material_date_query_params)
    response = as_point_managing_staff.get(  # type: ignore[no-untyped-call]
        reverse(
            "api_v1:companies:materials-statistic-list",
            kwargs={
                "company_pk": point_with_materials_statistic.company.id,
                "point_pk": point_with_materials_statistic.id,
            },
        ),
        data=material_date_query_params,
    )
    assert_rest_page(response, materials_statistic, MaterialsStatisticSerializer)


def test_materials_statistic_detail(
    as_point_managing_staff: StatusApiClient,
    point_with_materials_statistic: Point,
    material_date_query_params: dict[str, str],
):
    material = Material.objects.statistic(point_with_materials_statistic.id, **material_date_query_params).first()
    response = as_point_managing_staff.get(  # type: ignore[no-untyped-call]
        reverse(
            "api_v1:companies:materials-statistic-detail",
            kwargs={
                "company_pk": point_with_materials_statistic.company.id,
                "point_pk": point_with_materials_statistic.id,
                "pk": material.id,  # type: ignore[union-attr]
            },
        ),
        data=material_date_query_params,
    )
    assert response == MaterialsStatisticSerializer(material).data


def test_materials_statistic_usage_and_stocks_sort_by_date(
    as_point_managing_staff: StatusApiClient,
    point_with_materials_statistic: Point,
    material_date_query_params: dict[str, str],
):
    material = Material.objects.statistic(point_with_materials_statistic.id, **material_date_query_params).first()

    assert material

    response = as_point_managing_staff.get(  # type: ignore[no-untyped-call]
        reverse(
            "api_v1:companies:materials-statistic-detail",
            kwargs={
                "company_pk": point_with_materials_statistic.company.id,
                "point_pk": point_with_materials_statistic.id,
                "pk": material.id,
            },
        ),
        data=material_date_query_params,
    )
    for movement in [response["stocks"], response["usage"]]:
        assert all(elem1["date"] < elem2["date"] for elem1, elem2 in zip(movement, movement[1:]))


def test_materials_statistic_usage_and_stocks_filter_by_date(
    as_point_managing_staff: StatusApiClient,
    point_with_materials_statistic: Point,
    material_date_query_params: dict[str, str],
):
    def get_date(date: str) -> datetime:
        return datetime.strptime(date, "%Y-%m-%d")

    params = material_date_query_params
    material = Material.objects.statistic(point_with_materials_statistic.id, **params).first()

    assert material

    response = as_point_managing_staff.get(  # type: ignore[no-untyped-call]
        reverse(
            "api_v1:companies:materials-statistic-detail",
            kwargs={
                "company_pk": point_with_materials_statistic.company.id,
                "point_pk": point_with_materials_statistic.id,
                "pk": material.id,
            },
        ),
        data=params,
    )
    for movement in [response["stocks"], response["usage"]]:
        assert all(
            get_date(params["date_from"]) <= get_date(elem["date"]) <= get_date(params["date_to"]) for elem in movement
        )


@freeze_time("2022-01-01")
def test_materials_statistic_amount(
    as_point_managing_staff: StatusApiClient,
    point_with_materials_statistic: Point,
    material_date_query_params: dict[str, str],
):
    material_date_query_params["date_to"] = "2022-01-01"
    material = Material.objects.statistic(point_with_materials_statistic.id, **material_date_query_params).first()

    assert material

    url = reverse(
        "api_v1:companies:materials-statistic-detail",
        kwargs={
            "company_pk": point_with_materials_statistic.company.id,
            "point_pk": point_with_materials_statistic.id,
            "pk": material.id,
        },
    )
    response = as_point_managing_staff.get(url, data=material_date_query_params)  # type: ignore[no-untyped-call]
    stock_material = StockMaterial.objects.filter(material_id=material.id).order_by("stock__date").first()

    assert stock_material

    stock_material.stock.date = timezone.now().date()
    stock_material.stock.save()
    new_response = as_point_managing_staff.get(url, data=material_date_query_params)  # type: ignore[no-untyped-call]

    assert int(response["stocks"][0]["amount"]) - stock_material.quantity == int(new_response["stocks"][0]["amount"])


@freeze_time("2022-01-01")
def test_materials_statistic_usage_amount(
    as_point_managing_staff: StatusApiClient,
    point_with_materials_statistic: Point,
    material_date_query_params: dict[str, str],
):
    material_date_query_params["date_to"] = "2022-01-01"
    material = Material.objects.statistic(point_with_materials_statistic.id, **material_date_query_params).first()

    assert material

    url = reverse(
        "api_v1:companies:materials-statistic-detail",
        kwargs={
            "company_pk": point_with_materials_statistic.company.id,
            "point_pk": point_with_materials_statistic.id,
            "pk": material.id,
        },
    )
    response = as_point_managing_staff.get(url, data=material_date_query_params)  # type: ignore[no-untyped-call]
    used_material = UsedMaterial.objects.filter(material__material_id=material.id).order_by("created").first()

    assert used_material

    used_material.created = timezone.now()
    used_material.save()
    new_response = as_point_managing_staff.get(url, data=material_date_query_params)  # type: ignore[no-untyped-call]

    assert int(response["usage"][0]["amount"]) - used_material.amount == int(new_response["usage"][0]["amount"])
