from mainapp.objects.enums import DTOEnum
from mainapp.services.database import DatabaseManagement
from mainapp.objects.exceptions import DailyFavouriteDBObjectNotFound

import pytest
import datetime
from dataclasses import fields, is_dataclass
from typing import get_args, get_origin


@pytest.mark.django_db
class TestDatabase:
    USER_ID = 12345

    @pytest.mark.parametrize(
        "dto_type",
        [
            DTOEnum.USER,
            DTOEnum.GROUP,
            DTOEnum.MUSIC,
            DTOEnum.COMMENT,
            DTOEnum.POST,
            DTOEnum.VOTE,
        ],
    )
    def test_create_get_delete(self, dto_type: DTOEnum):
        """
        Tests create_or_get and create_or_update too
        """
        object_id = 1234
        dto = dto_type.getDTO()

        test_object = create_dummy_instance(dto)
        test_object.id = object_id

        dbm = DatabaseManagement(self.USER_ID)
        dbm.create_or_update(test_object, dto_type)
        test_dto = dbm.get(id=test_object.id, type=dto_type)

        assert test_dto is not None
        assert type(test_dto) is dto
        if dto_type == DTOEnum.MUSIC:
            assert test_dto.id == str(object_id)
        else:
            assert test_dto.id == object_id

        for f in fields(test_dto):
            assert f is not None

        # delete
        dbm.delete(test_dto, dto_type)

        with pytest.raises(DailyFavouriteDBObjectNotFound):
            dbm.get(id=test_object.id, type=dto_type)


# Helpers
def create_dummy_instance(cls):
    return cls(**{f.name: dummy_value(f.type) for f in fields(cls)})


def dummy_value(field_type):
    origin = get_origin(field_type)
    args = get_args(field_type)

    if origin is list:
        return [dummy_value(args[0])] if args else []
    if field_type is int:
        return 1
    if field_type is str:
        return "test"
    if field_type is bool:
        return True
    if field_type is datetime.datetime:
        return datetime.datetime.now()
    if is_dataclass(field_type):
        return create_dummy_instance(field_type)
    return None
