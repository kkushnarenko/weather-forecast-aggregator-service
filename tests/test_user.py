import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from src.main import app
from src.database import Base, get_db
import src.models

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_register_user_success():
    response = client.post("/weather/users/register?username=testuser")
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert "id" in data

def test_register_user_fail():
    client.post("/weather/users/register?username=testuser")
    response = client.post("/weather/users/register?username=testuser")
    assert response.status_code == 400


def test_add_and_get_cities_from_user():
    user_res = client.post("/weather/users/register?username=alice")
    user_id = user_res.json()["id"]

    add_res = client.post(
        f"/weather/cities?name=Moscow&latitude=55.75&longitude=37.61&user_id={user_id}"
    )
    assert add_res.status_code == 201

    get_res = client.get(f"/weather/cities?user_id={user_id}")
    assert get_res.status_code == 200
    cities = get_res.json()
    assert len(cities) == 1
    assert cities[0]["name"] == "Moscow"

