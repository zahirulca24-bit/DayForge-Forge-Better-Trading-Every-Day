import base64
import hashlib
import hmac
import secrets
from typing import Any

from itsdangerous import BadSignature, URLSafeSerializer

from app.config import settings


def is_auth_configured() -> bool:
    return bool(settings.admin_username and settings.admin_password_hash and settings.session_secret)


def _serializer() -> URLSafeSerializer:
    if not settings.session_secret:
        raise RuntimeError("SESSION_SECRET is not configured")
    return URLSafeSerializer(settings.session_secret, salt="session-token")


def verify_password(password: str, stored_hash: str) -> bool:
    """
    Supported format:
    pbkdf2_sha256$<iterations>$<salt>$<base64_digest>
    """
    try:
        algorithm, iterations, salt, expected = stored_hash.split("$", 3)
    except ValueError:
        return False

    if algorithm != "pbkdf2_sha256":
        return False

    derived = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        int(iterations),
    )
    actual = base64.b64encode(derived).decode("utf-8")
    return hmac.compare_digest(actual, expected)


def authenticate_admin(username: str, password: str) -> bool:
    if not is_auth_configured():
        return False
    if not hmac.compare_digest(username, settings.admin_username):
        return False
    return verify_password(password, settings.admin_password_hash)


def create_session_token(username: str) -> tuple[str, str]:
    if not settings.session_secret:
        raise ValueError("SESSION_SECRET is not configured")
    token_id = secrets.token_urlsafe(16)
    payload: dict[str, Any] = {"sub": username, "tid": token_id}
    token = _serializer().dumps(payload)
    return token, token_id


def verify_session_token(token: str) -> dict[str, Any]:
    try:
        payload = _serializer().loads(token)
    except BadSignature as exc:
        raise ValueError("Invalid token") from exc

    if not isinstance(payload, dict) or "sub" not in payload or "tid" not in payload:
        raise ValueError("Invalid token payload")

    return payload
