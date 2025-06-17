from mainapp.objects.dtos import ModelDTO, UserDTO
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
        model_class = type.getModel()
        defaults = self._dto_to_defaults(dto)

        # Lookup für UserMeta anders
        if model_class.__name__ == "UserMeta":
            lookup_kwargs = {'user_id': dto.id}  # dto.id ist hier die User.id
        else:
            lookup_kwargs = {'id': dto.id}

        try:
            obj, created = model_class.objects.update_or_create(defaults=defaults, **lookup_kwargs)
            return obj
        except Exception as e:
            raise DailyFavouriteDBObjectCouldNotBeCreated(dto, e)

    def get(self, id: str | int, type: DTOEnum) -> ModelDTO:
        model_class = type.getModel()

        # Lookup für UserMeta anders
        if model_class.__name__ == "UserMeta":
            lookup_kwargs = {'user_id': id}
        else:
            lookup_kwargs = {'id': id}

        try:
            model = model_class.objects.get(**lookup_kwargs)
        except Exception:
            raise DailyFavouriteDBObjectNotFound(type, id)

        serializer = type.getSerializer()(model)
        dto = type.getDTO()

        return dto(**serializer.data)

    def get_or_create(self, dto: ModelDTO, type: DTOEnum) -> Any:
        model_class = type.getModel()
        defaults = self._dto_to_defaults(dto)

        if model_class.__name__ == "UserMeta":
            lookup_kwargs = {'user_id': dto.id}
        else:
            lookup_kwargs = {'id': dto.id}

        try:
            obj, created = model_class.objects.get_or_create(defaults=defaults, **lookup_kwargs)
            return obj
        except Exception as e:
            raise DailyFavouriteDBObjectCouldNotBeCreated(dto, e)

    def list(
        self, attribute_value: str | int, type: DTOEnum, filter_attr: str = "id"
    ) -> List[ModelDTO]:
        model_class = type.getModel()

        field_names = [field.name for field in model_class._meta.get_fields()]
        if (
            filter_attr.split("_")[0] not in field_names
            and filter_attr not in field_names
        ):
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
        model_class = type.getModel()

        if model_class.__name__ == "UserMeta":
            model_class.objects.filter(user_id=dto.id).delete()
        else:
            model_class.objects.filter(id=dto.id).delete()

    # Helpers
    def _dto_to_defaults(self, dto: ModelDTO) -> dict:
        if isinstance(dto, UserDTO):
            return {
                'profile_picture': dto.profile_picture,
                'favorite_artist': dto.favorite_artist,
                'favorite_genre': dto.favorite_genre,
            }

        # Generischer Code für andere DTOs
        defaults = {}
        for field in fields(dto):
            value = getattr(dto, field.name)
            if is_dataclass(value):
                inner_model = self.get_or_create(value, DTOEnum.fromDTO(value))
                defaults[field.name] = inner_model
            else:
                defaults[field.name] = value
        return defaults

