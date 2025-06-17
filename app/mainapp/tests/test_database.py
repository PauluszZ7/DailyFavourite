from django.contrib.auth.models import User

@pytest.mark.django_db
class TestDatabase:
    USER_ID = 12345

    def setup_user(self):
        # Lege einen User an, den du als Foreign Key verwenden kannst
        user, created = User.objects.get_or_create(id=self.USER_ID, defaults={
            "username": "testuser",
            "password": "password123",
        })
        return user

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
        # User anlegen
        user = self.setup_user()

        object_id = 1234
        dto = dto_type.getDTO()

        test_object = create_dummy_instance(dto)
        test_object.id = object_id

        # Wenn das DTO ein ForeignKey auf User erwartet,
        # dann muss test_object.user (oder user_id) auf user gesetzt werden
        # Beispiel:
        if hasattr(test_object, "user"):
            test_object.user.id = user.id
        elif hasattr(test_object, "user_id"):
            test_object.user_id = user.id

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
