from sqlalchemy.orm import Session
from app.services import UserService
from app.models import UserModel
from app.models.user import UserType
from app.core.config import settings
from app.core.exceptions import AppstoreUserNotFoundException, AppstoreUserDoesNotMatchException, AppstoreUnsupportedUserTypeException, UserNotFoundException
import httpx

class AppstoreService:
    def __init__(self, session: Session, appstore_identity_token: str, user_type: UserType):
        self.session = session
        self.user_type = user_type
        self.client = httpx.AsyncClient(
            base_url=f"{ self.base_url }",
            headers={
                "User-Agent": f"eduhelx_grader_api",
                "Authorization": f"Bearer { appstore_identity_token }"
            },
            timeout=httpx.Timeout(10)
        )

    @property
    def base_url(self) -> str:
        if self.user_type == UserType.STUDENT:
            return settings.STUDENT_APPSTORE_HOST
        elif self.user_type == UserType.INSTRUCTOR:
            return settings.INSTRUCTOR_APPSTORE_HOST
        raise AppstoreUnsupportedUserTypeException()
        
    async def _make_request(self, method: str, endpoint: str, headers={}, **kwargs):
        res = await self.client.request(
            method,
            endpoint,
            headers={
                **headers
            },
            **kwargs
        )
        res.raise_for_status()
        return res

    async def _get(self, endpoint: str, **kwargs):
        return await self._make_request("GET", endpoint, **kwargs)

    async def _post(self, endpoint: str, **kwargs):
        return await self._make_request("POST", endpoint, **kwargs)
    
    async def get_remote_user(self) -> str:
        try:
            res = await self._get("auth/identity/", follow_redirects=False)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise AppstoreUserNotFoundException()
            else:
                raise e
        
        remote_user = res.headers.get("REMOTE_USER")
        if not remote_user:
            raise AppstoreUserNotFoundException()
        return remote_user
    
    async def get_associated_eduhelx_user(self) -> UserModel:
        remote_user = await self.get_remote_user()
        try:
            return await UserService(self.session).get_user_by_onyen(remote_user)
        except UserNotFoundException:
            raise AppstoreUserDoesNotMatchException(message=f'appstore user "{ remote_user }" does not have an associated eduhelx account')
