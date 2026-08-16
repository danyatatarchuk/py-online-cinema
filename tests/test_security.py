from datetime import datetime, timedelta, timezone

import pytest
from jose import jwt

from app.core.security import (
    ALGORITHM,
    SECRET_KEY,
    create_access_token,
    create_refresh_token,
    decode_token,
)


def test_create_access_token():
    token = create_access_token(1)

    payload = jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM],
    )

    assert payload["sub"] == "1"
    assert payload["type"] == "access"
    assert "exp" in payload


def test_create_refresh_token():
    token = create_refresh_token(1)

    payload = jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM],
    )

    assert payload["sub"] == "1"
    assert payload["type"] == "refresh"
    assert "exp" in payload


def test_decode_token():
    token = create_access_token(1)

    payload = decode_token(token)

    assert payload["sub"] == "1"
    assert payload["type"] == "access"


def test_decode_invalid_token():
    with pytest.raises(ValueError, match="Invalid or expired token"):
        decode_token("invalid-token")


def test_decode_expired_token():
    payload = {
        "sub": "1",
        "type": "access",
        "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
    }

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    with pytest.raises(ValueError, match="Invalid or expired token"):
        decode_token(token)
