import pytest
import requests
from fastapi.testclient import TestClient

from main import app, Course  

client = TestClient(app)

def test_get_courses():
    response = client.get("/courses/alphabetical")  
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    
    for item in data:
        assert isinstance(item, Course)
        assert item.name is not None
