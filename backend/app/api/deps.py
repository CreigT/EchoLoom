from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.security.auth import decode_token

bearer = HTTPBearer(auto_error=False)


async def current_user_optional(creds: HTTPAuthorizationCredentials | None = Depends(bearer)) -> dict | None:
    if creds is None:
        return None
    try:
        return decode_token(creds.credentials)
    except ValueError:
        return None


async def current_user(creds: HTTPAuthorizationCredentials | None = Depends(bearer)) -> dict:
    user = await current_user_optional(creds)
    if user is None:
        raise HTTPException(status_code=401, detail="Sign in to the studio first")
    return user
