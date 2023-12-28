from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.viewsets import ModelViewSet

from django.db.models import QuerySet

from app.api.permissions import IsCompanyOwnerOrReadOnly
from companies.api.serializers import EmployeeSerializer
from companies.models.employee import Employee


@extend_schema(
    tags=["employees"],
    parameters=[
        OpenApiParameter("company_pk", OpenApiTypes.INT, OpenApiParameter.PATH),
        OpenApiParameter("point_pk", OpenApiTypes.INT, OpenApiParameter.PATH),
    ],
)
class EmployeeViewSet(ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly, IsCompanyOwnerOrReadOnly]
    queryset = Employee.objects.none()  # for swagger schema
    serializer_class = EmployeeSerializer

    def get_queryset(self) -> QuerySet[Employee]:
        return Employee.objects.filter(
            departments__point__company_id=self.kwargs["company_pk"],
            departments__point_id=self.kwargs["point_pk"],
        )
