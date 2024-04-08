import pytest
from datetime import datetime, timedelta

from freezegun import freeze_time

from django.utils import timezone

from app.testing import FixtureFactory
from companies.models import Point, Procedure


@pytest.fixture
def material_date_query_params() -> dict[str, str]:
    return {"date_from": "2000-01-01", "date_to": "2002-01-01"}


@pytest.fixture(
    params=[
        {"date_from": "2000-01-01", "date_to": "2222"},
        {"date_from": "2222-01-01", "date_to": "2002-01-01"},
        {"date_from": "2001-01-01", "date_to": "2001-01-01"},
    ]
)
def invalide_material_date_query_params(request: pytest.FixtureRequest) -> dict[str, str]:
    return request.param


def create_point_with_materials_statistic(
    factory: FixtureFactory,
    procedure: Procedure,
    now: datetime,
    timedelta_stock_material: int,
    quantity_stock_material: int,
    quantity_used_material: int,
) -> None:
    stock_materials = []
    point = procedure.department.point
    for date in [now + timedelta(days=timedelta_stock_material * i) for i in range(4)]:
        stock_material = factory.stock_material(
            stock=factory.stock(point=point, date=date.date()),
        )
        stock_materials.append(stock_material)
        iter_date = [date.date()] + [date.date() + timedelta(days=i) for i in range(1, quantity_stock_material)]
        for created_date in iter_date:
            stock_materials.append(
                factory.stock_material(
                    stock=factory.stock(point=point, date=created_date),
                    material=stock_material.material,
                )
            )
    iter_datetime = [now] + [now + timedelta(days=i) for i in range(quantity_used_material)]
    for created_date in iter_datetime:
        for stock_material in stock_materials:
            with freeze_time(created_date):
                factory.used_material(
                    procedure=factory.purchase_procedure(procedure=procedure),
                    material=stock_material,
                )


@pytest.fixture
@freeze_time("2000-01-01 10:23:40")
def point_with_materials_statistic(factory: FixtureFactory, procedure: Procedure) -> Point:
    now = timezone.now()
    point = procedure.department.point
    create_point_with_materials_statistic(factory, procedure, now, 100, 6, 10)
    return point


@pytest.fixture
@freeze_time("2000-01-01 10:23:40")
def point_with_materials_statistic_the_same_period(factory: FixtureFactory) -> Point:
    now = timezone.now()
    procedure = factory.procedure(department=factory.department())
    point = procedure.department.point
    create_point_with_materials_statistic(factory, procedure, now, 100, 5, 15)
    return point


@pytest.fixture
@freeze_time("2000-01-01 10:23:40")
def point_with_materials_statistic_30_days(factory: FixtureFactory) -> Point:
    now = timezone.now()
    procedure = factory.procedure(department=factory.department())
    point = procedure.department.point
    create_point_with_materials_statistic(factory, procedure, now, 15, 4, 20)
    return point


@pytest.fixture
def point_without_materials_statistic(factory: FixtureFactory) -> Point:
    return factory.company_point()


@pytest.fixture
def quantity_materials_in_stocks(
    point_with_materials_statistic: Point,
    point_with_materials_statistic_the_same_period: Point,
    point_with_materials_statistic_30_days: Point,
    point_without_materials_statistic: Point,
) -> dict[Point, dict[str, int]]:
    return {
        point_with_materials_statistic: {"stocks": 6, "usage": 10},
        point_with_materials_statistic_the_same_period: {"stocks": 5, "usage": 15},
        point_with_materials_statistic_30_days: {"stocks": 4, "usage": 20},
        point_without_materials_statistic: {"stocks": 0, "usage": 0},
    }
