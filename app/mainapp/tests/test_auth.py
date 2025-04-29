import pytest 

@pytest.mark.django_db
def test_dummy():
    assert 200 == 200
