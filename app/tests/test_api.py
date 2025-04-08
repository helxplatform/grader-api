import pytest

#################
# Miscellaneous #
#################
def test_readiness(test_client):
    response = test_client.get("/")
    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}


######################
# Test course router #
######################
@pytest.mark.parametrize("user_client", ["basicstudent", "basicinstructor"], indirect=True)
def test_get_course(user_client):
    from .data.database.course import course
    from .data.database.instructor import data as instructors
    response = user_client.get("/api/v1/course")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == course.name
    assert len(data["instructors"]) == len(instructors)