from datetime import timedelta
from typing import Self

from django.contrib.postgres.expressions import ArraySubquery
from django.db import models
from django.db.models import F, OuterRef, Q, QuerySet, Sum
from django.db.models.functions import JSONObject, TruncDate
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from app.models import DefaultModel
from companies.models.stock import StockMaterial
from purchases.models import UsedMaterial


class MaterialType(DefaultModel):
    name = models.CharField(
        _("material type name"),
        max_length=255,
    )

    class Meta:
        ordering = ("name",)
        verbose_name = _("material type")
        verbose_name_plural = _("material types")


class MaterialQuerySet(QuerySet):
    def statistic(self, point_id: int, date_from: str | None = None, date_to: str | None = None) -> Self:
        now = timezone.now().date()
        date_filter = Q(date__gte=date_from or (now - timedelta(days=30))) & Q(date__lte=date_to or now)
        stock_queryset = (
            StockMaterial.objects.select_related("stock__date")
            .filter(stock__point__id=point_id)
            .annotate(date=F("stock__date"))
            .filter(date_filter)
        )
        stocks = (
            stock_queryset.filter(material_id=OuterRef("id"))
            .order_by("date")
            .values("material_id", "date")
            .annotate(amount=Sum("quantity"))
            .annotate(  # noqa: BLK100
                stocks=JSONObject(
                    date=F("date"),
                    amount=F("amount")
                )
            )
            .values_list("stocks", flat=True)
        )
        usage_queryset = (
            UsedMaterial.objects
            .filter(material__stock__point_id=point_id)
            .select_related("material__material_id")
            .annotate(date=TruncDate("modified"))
            .filter(date_filter)
        )
        usage = (
            usage_queryset.filter(material__material_id=OuterRef("id"))
            .order_by("date")
            .values("material__material_id", "date")
            .annotate(amount=Sum("amount"))
            .annotate(
                stocks=JSONObject(
                    date=F("date"),
                    amount=F("amount")
                )
            )
            .values_list("stocks", flat=True)
        )
        material_ids = set(
            list(
                stock_queryset.values_list("material_id", flat=True)
            ) + list(
                usage_queryset.values_list("material_id", flat=True)
            )
        )
        return self.filter(id__in=material_ids).annotate(
            stocks=ArraySubquery(stocks), usage=ArraySubquery(usage)
        )


class Material(DefaultModel):
    brand = models.CharField(
        _("material brand"),
        max_length=255,
    )
    name = models.CharField(
        _("material name"),
        max_length=255,
    )
    unit = models.CharField(
        _("material unit"),
        max_length=255,
    )
    kind = models.ForeignKey(
        "MaterialType",
        on_delete=models.PROTECT,
        related_name="materials",
    )

    objects = MaterialQuerySet.as_manager()

    class Meta:
        ordering = ("name",)
        verbose_name = _("material")
        verbose_name_plural = _("materials")
