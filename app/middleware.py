from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.auth import verify_session_token
from app.database import SessionLocal
from app.models import UserSession


class AuthMiddleware(BaseHTTPMiddleware):
    protected_paths = {
        "/session/verify",
        "/account",
    }

    async def dispatch(self, request: Request, call_next):
        request.state.session = None

        # Let CORS preflight requests pass through untouched.
        if request.method.upper() == "OPTIONS":
            return await call_next(request)

        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.removeprefix("Bearer ").strip()
            try:
                payload = verify_session_token(token)
                db = SessionLocal()
                try:
                    session_row = (
                        db.query(UserSession)
                        .filter(
                            UserSession.username == payload["sub"],
                            UserSession.token_id == payload["tid"],
                        )
                        .first()
                    )
                finally:
                    db.close()

                if session_row is not None:
                    request.state.session = payload
            except (RuntimeError, ValueError):
                request.state.session = None

        if request.url.path in self.protected_paths and request.state.session is None:
            return JSONResponse(status_code=401, content={"detail": "Unauthorized"})

        return await call_next(request)
