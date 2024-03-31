from dataclasses import dataclass
from datetime import datetime
from typing import Callable

from rest_framework.exceptions import ValidationError
from rest_framework.request import Request

from app.services import BaseService


@dataclass
class DateValidatorService(BaseService):
    request: Request

    def valide_date_query_params(self) -> None:
        query_params = self.request.query_params
        if not query_params:
            return
        try:
            date_format = "%Y-%m-%d"
            date_from_str = query_params.get("date_from")
            date_to_str = query_params.get("date_to")
            if date_from_str:
                date_from = datetime.strptime(date_from_str, date_format).date()
            if date_to_str:
                date_to = datetime.strptime(date_to_str, date_format).date()
            if date_from_str and date_to_str and date_from >= date_to:
                raise ValidationError("date_from must be less than the date_to.")
        except (TypeError, ValueError):
            raise ValidationError("Invalid date format.")

    def get_validators(self) -> list[Callable]:
        return super().get_validators() + [self.valide_date_query_params]

    def act(self) -> bool:
        return True
