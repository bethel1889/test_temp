import pytest
from typing import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from src.main import app
from src.database.core import Base, get_db

# --- Test Database Configuration ---
# Use an in-memory SQLite database for testing. It's fast and isolated.
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

# Create a new SQLAlchemy engine for the test database.
# `connect_args` is specific to SQLite to allow the same connection to be used across threads.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create a session factory for the test database.
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Fixture Definitions ---

@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """
    Pytest fixture to create and manage a test database session for each test function.
    
    - Creates all database tables before the test runs.
    - Yields a database session to the test.
    - Drops all database tables after the test completes.
    """
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
    
    # Drop tables
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """
    Pytest fixture to provide an API test client.
    
    This fixture overrides the `get_db` dependency for the entire application
    with a version that provides the isolated, in-memory test database session.
    """

    def override_get_db() -> Generator[Session, None, None]:
        """Dependency override for get_db that uses the test database session."""
        try:
            yield db_session
        finally:
            db_session.close()

    # Apply the dependency override
    app.dependency_overrides[get_db] = override_get_db

    # Yield the TestClient
    with TestClient(app) as c:
        yield c

    # Clean up the dependency override after the test
    app.dependency_overrides.clear()