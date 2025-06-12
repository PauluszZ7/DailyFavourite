from mainapp.objects.enums import DTOEnum
from mainapp.services.database import DatabaseManagement
from mainapp.objects.exceptions import DailyFavouriteDBObjectNotFound
from mainapp.objects.dtos import ModelDTO

from django.db import models

import pytest
from dataclasses import fields

from mainapp.tests.helpers import TEST_DATE, create_dummy_instance


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
    def test_list(self, dto_type: DTOEnum):
        """
        Tests list of DTO Objects
        """
        object_id = 1234
        dto = dto_type.getDTO()

        test_object = create_dummy_instance(dto)
        test_object.id = object_id

        dbm = DatabaseManagement(self.USER_ID)
        dbm.get_or_create(test_object, dto_type)

        test_object.id += 1
        # Spezialfall VOTE: User und Music nicht doppelt.
        if dto_type == DTOEnum.VOTE:
            test_object.user.id += 1
        dbm.get_or_create(test_object, dto_type)

        fieldname, value = get_first_test_field_and_value(test_object)
        dto_objects = dbm.list(value, dto_type, fieldname)

        assert len(dto_objects) == 2
        assert type(dto_objects[0]) is dto_type.getDTO()
        assert type(dto_objects[1]) is dto_type.getDTO()

        assert dto_objects[0].id == object_id or dto_objects[0].id == str(object_id)
        assert dto_objects[1].id == object_id + 1 or dto_objects[1].id == str(
            object_id + 1
        )


# Helpers
def get_first_test_field_and_value(dto: ModelDTO):
    model_class = DTOEnum.fromDTO(dto).getModel()

    for field in model_class._meta.fields:
        if field.name == "id":
            continue
        if isinstance(field, models.CharField):
            return field.name, "test"
        if isinstance(field, models.IntegerField):
            return field.name, 1
        if isinstance(field, models.DateTimeField):
            return field.name, TEST_DATE
        if isinstance(field, models.BooleanField):
            return field.name, True

    raise ValueError(f"No suitable field found for DTO: {dto}")
