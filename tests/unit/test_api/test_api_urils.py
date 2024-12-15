import pytest
from fastapi.testclient import TestClient
from src.api.utils import router

@pytest.fixture
def client():
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)

def test_healthcheck(client):
    response = client.get("/healthcheck/")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "API is working"}
