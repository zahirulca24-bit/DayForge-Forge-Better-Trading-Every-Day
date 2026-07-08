from fastapi import HTTPException, Request, status


def require_authenticated(request: Request) -> dict:
    session = getattr(request.state, "session", None)
    if session is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return session
