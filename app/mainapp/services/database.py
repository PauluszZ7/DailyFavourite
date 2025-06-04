from mainapp.objects.dtos import ModelDTO
from mainapp.objects.enums import DTOEnum
from mainapp.objects.exceptions import (
    DailyFavouriteDBObjectCouldNotBeCreated,
    DailyFavouriteDBObjectNotFound,
)

from typing import Any
from dataclasses import is_dataclass, fields


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
