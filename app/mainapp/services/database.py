from mainapp.objects.dtos import ModelDTO
from mainapp.objects.enums import DTOEnum
from mainapp.objects.exceptions import (
    DailyFavouriteDBAttributeNotFound,
    DailyFavouriteDBObjectCouldNotBeCreated,
    DailyFavouriteDBObjectNotFound,
)

from typing import Any, List
from dataclasses import is_dataclass, fields
from django.db import models

import datetime


class DatabaseManagement:
    current_user: str

    def __init__(self, current_user) -> None:
        self.current_user = current_user

    def create_or_update(self, dto: ModelDTO, type: DTOEnum) -> None:
        """
        Does NOT update inner dtos (Foreign Keys).
        """
        try:
            model = type.getModel()
            defaults = self._dto_to_defaults(dto)

            obj, created = model.objects.update_or_create(id=dto.id, defaults=defaults)
            return obj
        except Exception as e:
            raise DailyFavouriteDBObjectCouldNotBeCreated(dto, e)

    def get(self, id: str | int, type: DTOEnum) -> ModelDTO:
        try:
            model = type.getModel().objects.get(id=id)
        except Exception:
            raise DailyFavouriteDBObjectNotFound(type, id)

        serializer = type.getSerializer()(model)
        dto = type.getDTO()

        return dto(**serializer.data)

    def get_or_create(self, dto: ModelDTO, type: DTOEnum) -> Any:
        try:
            model = type.getModel()
            defaults = self._dto_to_defaults(dto)

            obj, created = model.objects.get_or_create(id=dto.id, defaults=defaults)
            return obj
        except Exception as e:
            raise DailyFavouriteDBObjectCouldNotBeCreated(dto, e)

    def list(
        self, attribute_value: str, type: DTOEnum, filter_attr: str = "id"
    ) -> List[ModelDTO]:
        model_class = type.getModel()

        if filter_attr not in [field.name for field in model_class._meta.get_fields()]:
            raise DailyFavouriteDBAttributeNotFound(type.getDTO(), filter_attr)

        field = model_class._meta.get_field(filter_attr)

        # Spezial: Datetime wird nur nach Tag gefiltert.
        if isinstance(field, models.DateTimeField):
            if isinstance(attribute_value, datetime.datetime):
                attribute_value = attribute_value.date()
            queryset = model_class.objects.filter(
                **{f"{filter_attr}__date": attribute_value}
            )
        else:
            queryset = model_class.objects.filter(**{filter_attr: attribute_value})

        if not queryset.exists():
            raise DailyFavouriteDBObjectNotFound(type.getDTO(), id=0)

        serialized = type.getSerializer()(queryset, many=True)
        dtos = [type.getDTO()(**data) for data in serialized.data]
        return dtos

    def delete(self, dto: ModelDTO, type: DTOEnum) -> None:
        type.getModel().objects.filter(id=dto.id).delete()

    # Helpers
    def _dto_to_defaults(self, dto: ModelDTO) -> dict:
        defaults = {}
        for field in fields(dto):
            value = getattr(dto, field.name)

            if is_dataclass(value):
                # Rekursiv abspeichern, bevor wir's einsetzen
                inner_model = self.get_or_create(value, DTOEnum.fromDTO(value))
                defaults[field.name] = inner_model
            else:
                defaults[field.name] = value
        return defaults
