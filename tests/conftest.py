import os
import tempfile
from uuid import UUID

os.environ.setdefault("JWT_SECRET_KEY", "test-secret")
os.environ["DB_URL"] = f"sqlite://{os.path.join(tempfile.mkdtemp(), 'test.sqlite3')}"

import pytest
from fastapi.testclient import TestClient
from tortoise.contrib.test import truncate_all_models

from app.app import app
from app.config.storage import StorageConfig
from app.database.actions import create_case
from app.database.models import CaseDifficulty
from app.repository.factory import get_token_repository
from app.repository.local import LocalRepository
from app.services.mailer import ActivationMailer, get_activation_mailer


class FakeActivationMailer(ActivationMailer):
    def __init__(self):
        self.sent: list[tuple[str, str]] = []

    async def send_activation_link(self, *, email: str, code: str) -> None:
        self.sent.append((email, code))


@pytest.fixture(scope="session")
def _test_client_session():
    # Entering as a context manager fires the app's lifespan (register_tortoise,
    # pointed at our DB_URL override above) and keeps ONE portal thread alive for
    # every request, instead of spinning up and reconnecting a fresh one per call.
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
async def reset_db(_test_client_session):
    yield
    await truncate_all_models()


@pytest.fixture
async def case_uuid() -> UUID:
    case = await create_case(
        name="Test case",
        description="A case for tests",
        category="general",
        difficulty=CaseDifficulty.EASY,
        time_limit=30,
        system_prompt="You are a test persona",
        goal="Reach the goal",
        synopsis="A short synopsis",
        first_role="Detective",
        second_role="Suspect",
        first_role_preparations="Review the evidence",
        second_role_preparations="Prepare an alibi",
    )
    return case.uuid


@pytest.fixture
def local_repository() -> LocalRepository:
    repository = LocalRepository(StorageConfig())
    repository._store.clear()
    repository._expirations.clear()
    return repository


@pytest.fixture
def fake_mailer() -> FakeActivationMailer:
    return FakeActivationMailer()


@pytest.fixture
def client(
    _test_client_session: TestClient,
    local_repository: LocalRepository,
    fake_mailer: FakeActivationMailer,
):
    app.dependency_overrides[get_token_repository] = lambda: local_repository
    app.dependency_overrides[get_activation_mailer] = lambda: fake_mailer
    try:
        yield _test_client_session
    finally:
        app.dependency_overrides.clear()


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    # Tortoise's connection.py reconnects (without closing the old connection) whenever
    # it's accessed from a different task/thread than it was created on — unavoidable here
    # since TestClient dispatches on its own thread. Each reconnect leaks an idle,
    # harmless aiosqlite worker thread that otherwise blocks the interpreter from exiting.
    # All results are already reported by this point, so force the exit with pytest's
    # own exit code rather than hang waiting for those threads to join.
    os._exit(exitstatus)
