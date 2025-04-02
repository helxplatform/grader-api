import jwt
from typing import Optional, Tuple
from pydantic import BaseModel, Field
from starlette.authentication import AuthenticationBackend
from starlette.middleware.authentication import (
    AuthenticationMiddleware as BaseAuthenticationMiddleware,
)
from starlette.requests import HTTPConnection
from app.core.config import settings

class CurrentUser(BaseModel, validate_assignment=True):
    id: int = Field(None, description="ID of the current user")
    onyen: str = Field(None, description="Onyen of the current user")

class AuthBackend(AuthenticationBackend):
    async def authenticate(
        self, conn: HTTPConnection
    ) -> Tuple[bool, Optional[CurrentUser]]:
        current_user = CurrentUser()
        authorization: str = conn.headers.get("Authorization")
        
        if settings.DISABLE_AUTHENTICATION:
            return await self.handle_impersonated_auth()

        if not authorization:
            return False, current_user

        try:
            scheme, credentials = authorization.split(" ")
            if scheme.lower() != "bearer":
                return False, current_user
        except ValueError:
            return False, current_user

        if not credentials:
            return False, current_user

        try:
            payload = jwt.decode(
                credentials,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
            id = payload.get("id")
            onyen = payload.get("onyen")
        except jwt.exceptions.PyJWTError:
            return False, current_user

        current_user.id = id
        current_user.onyen = onyen
        return True, current_user
    
    async def handle_impersonated_auth(self):
        from app.database import SessionLocal
        from app.services import UserService
        from app.core.exceptions import UserNotFoundException

        current_user = CurrentUser()

        if settings.IMPERSONATE_USER is None:
            return False, current_user
        
        with SessionLocal() as session:
            try:
                user = await UserService(session).get_user_by_onyen(settings.IMPERSONATE_USER)
                current_user.id = user.id
                current_user.onyen = user.onyen
                return True, current_user
            except UserNotFoundException:
                return False, current_user



class AuthenticationMiddleware(BaseAuthenticationMiddleware):
    pass