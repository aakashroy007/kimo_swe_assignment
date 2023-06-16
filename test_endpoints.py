import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_get_courses_alphabetical():
    response = client.get("/courses?mode=alphabetical")
    assert response.status_code == 200
    assert "courses" in response.json()


def test_get_courses_date():
    response = client.get("/courses?mode=date")
    assert response.status_code == 200
    assert "courses" in response.json()


def test_get_courses_rating():
    response = client.get("/courses?mode=rating")
    assert response.status_code == 200
    assert "courses" in response.json()


def test_get_course_overview():
    response = client.get("/course_overview/Highlights%20of%20Calculus")
    assert response.status_code == 200
    assert "course_overview" in response.json()


def test_get_chapter_info():
    response = client.get(
        "/chapter_info/Highlights%20of%20Calculus/Big%20Picture%20of%20Calculus"
    )
    assert response.status_code == 200
    assert "chapter_information" in response.json()


def test_rate_chapter():
    response = client.post(
        "/rate_chapter/Highlights%20of%20Calculus/Big%20Picture%20of%20Calculus/1"
    )
    assert response.status_code == 200
    assert "message" in response.json()
    assert "course_rating" in response.json()


if __name__ == "__main__":
    pytest.main()
