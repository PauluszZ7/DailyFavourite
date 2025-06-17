from django.contrib.auth.models import User
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
    @pytest.fixture(autouse=True)
    def setup_users(self):
        # Create a test user that will be used across all tests
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.USER_ID = self.user.id  # Use dynamic ID instead of hardcoded

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
        # Create test object with proper relationships
        test_object = create_dummy_instance(dto_type.getDTO())

        # For User DTO, ensure it uses our test user
        if dto_type == DTOEnum.USER:
            test_object.id = self.user.id
            test_object.username = self.user.username

        dbm = DatabaseManagement(self.USER_ID)

        # Create/update
        created_dto = dbm.create_or_update(test_object, dto_type)

        # Verify creation
        assert created_dto is not None
        assert isinstance(created_dto, dto_type.getDTO())

        # Verify get
        fetched_dto = dbm.get(id=created_dto.id, type=dto_type)
        assert fetched_dto is not None

        # Verify fields
        for field in fields(fetched_dto):
            assert getattr(fetched_dto, field.name) is not None

        # Test deletion
        dbm.delete(fetched_dto, dto_type)

        # Verify deletion
        with pytest.raises(DailyFavouriteDBObjectNotFound):
            dbm.get(id=created_dto.id, type=dto_type)

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
        dbm = DatabaseManagement(self.USER_ID)

        # Create two test instances
        instance1 = create_dummy_instance(dto_type.getDTO())
        instance2 = create_dummy_instance(dto_type.getDTO())

        # For User DTO, use our test user
        if dto_type == DTOEnum.USER:
            instance1.id = self.user.id
            instance2.id = self.user.id + 1  # Different ID

        dbm.create_or_update(instance1, dto_type)
        dbm.create_or_update(instance2, dto_type)

        # Get field to filter by
        fieldname, value = get_first_test_field_and_value(instance1)

        # Special case for Vote - needs different users
        if dto_type == DTOEnum.VOTE:
            fieldname = "user"
            value = self.user.id

        results = dbm.list(value, dto_type, fieldname)

        # Verify results
        assert len(results) >= 1  # At least one should match
        assert all(isinstance(r, dto_type.getDTO()) for r in results)


def get_first_test_field_and_value(dto: ModelDTO):
    model_class = DTOEnum.fromDTO(dto).getModel()

    for field in model_class._meta.fields:
        if field.name == "id":
            continue
        if isinstance(field, models.ForeignKey):
            return field.name, 1  # Default to ID 1 for foreign keys
        if isinstance(field, models.CharField):
            return field.name, "test"
        if isinstance(field, models.IntegerField):
            return field.name, 1
        if isinstance(field, models.DateTimeField):
            return field.name, TEST_DATE
        if isinstance(field, models.BooleanField):
            return field.name, True

    raise ValueError(f"No suitable field found for DTO: {dto}")