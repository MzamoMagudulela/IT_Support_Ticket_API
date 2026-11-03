import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

os.environ["TESTING"] = "true"
os.environ["DATABASE_URL"] = "sqlite:///./test_enterprise_itsm.db"

from app.core.database import Base, get_db
from app.core.security import create_access_token
from app.db.seed_data import seed_database
from app.main import app

engine = create_engine("sqlite:///./test_enterprise_itsm.db", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    seed_database(db)
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("./test_enterprise_itsm.db"):
        try:
            os.remove("./test_enterprise_itsm.db")
        except Exception:
            pass

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def admin_token():
    return create_access_token(subject="admin", roles=["System Administrator"], user_id=1)

@pytest.fixture
def employee_token():
    return create_access_token(subject="john.employee", roles=["Employee"], user_id=4)

@pytest.fixture
def manager_token():
    return create_access_token(subject="sarah.manager", roles=["IT Operations Manager"], user_id=2)

@pytest.fixture
def technician_token():
    return create_access_token(subject="alex.tech", roles=["IT Support Technician"], user_id=3)
