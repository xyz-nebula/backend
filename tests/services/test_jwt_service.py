from datetime import UTC, datetime, timedelta

import pytest

from app.services.JWTService import JWTService


@pytest.fixture
def jwt_service() -> JWTService:
    return JWTService(secret_key="test-secret", algorithm="HS256")


def test_encode_decode_roundtrip(jwt_service: JWTService):
    token = jwt_service.encode(sub="user-123", expires_delta=timedelta(minutes=5))
    payload = jwt_service.decode(token)
    assert payload.sub == "user-123"


def test_expired_token_raises(jwt_service: JWTService):
    past = datetime.now(UTC) - timedelta(hours=1)
    token = jwt_service.encode(sub="user-123", expires_delta=timedelta(minutes=5), now=past)
    with pytest.raises(ValueError):
        jwt_service.decode(token)


def test_wrong_secret_raises(jwt_service: JWTService):
    token = jwt_service.encode(sub="user-123", expires_delta=timedelta(minutes=5))
    other = JWTService(secret_key="different-secret", algorithm="HS256")
    with pytest.raises(ValueError):
        other.decode(token)


def test_malformed_token_raises(jwt_service: JWTService):
    with pytest.raises(ValueError):
        jwt_service.decode("not-a-real-token")
