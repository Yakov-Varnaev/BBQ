from django.db import models
from django.utils.translation import gettext_lazy as _

from app.models import DefaultModel


class Department(models.Model):
    point = models.ForeignKey(
        "companies.Point", on_delete=models.CASCADE, related_name="departments", verbose_name=_("point")
    )
    name = models.CharField(_("department name"), max_length=255)

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ("name",)
        verbose_name = _("department")
        verbose_name_plural = _("departments")


class Procedure(DefaultModel):
    name = models.CharField(_("procedure name"), max_length=255)
    kind = models.ForeignKey(
        "companies.MaterialType", on_delete=models.CASCADE, related_name="procedures", verbose_name=_("material type")
    )
    department = models.ForeignKey(
        "Department", on_delete=models.CASCADE, related_name="procedures", verbose_name=_("department")
    )

    class Meta:
        ordering = ("name",)
        verbose_name = _("procedure")
        verbose_name_plural = _("procedures")
