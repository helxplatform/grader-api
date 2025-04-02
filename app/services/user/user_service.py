from sqlalchemy.orm import Session
from src.events import dispatch
from src.models import UserModel, AutoPasswordAuthModel
from src.events import DeleteUserCrudEvent
from src.schemas import RefreshTokenSchema
from src.core.config import settings
from src.core.utils.token_helper import TokenHelper
from src.core.utils.auth_helper import PasswordHelper
from src.core.middleware.authentication import CurrentUser
from src.core.exceptions import (
    PasswordDoesNotMatchException,
    UserNotFoundException,
    PasswordDoesNotMatchException
)

class UserService:
    def __init__(self, session: Session):
        self.session = session

    async def get_user_by_id(self, id: int) -> UserModel:
        user = self.session.query(UserModel).filter_by(id=id).first()
        if user is None:
            raise UserNotFoundException()
        return user

    async def get_user_by_onyen(self, onyen: str) -> UserModel:
        user = self.session.query(UserModel).filter_by(onyen=onyen).first()
        if user is None:
            raise UserNotFoundException()
        return user

    async def get_user_by_email(self, email: str) -> UserModel:
        user = self.session.query(UserModel).filter_by(email=email).first()
        if user is None:
            raise UserNotFoundException()
        return user
    
    async def _create_user_token(self, user: UserModel) -> RefreshTokenSchema:
        current_user = CurrentUser(id=user.id, onyen=user.onyen)

        response = RefreshTokenSchema(
            access_token=TokenHelper.encode(payload=current_user.dict(), expire_period=settings.ACCESS_TOKEN_EXPIRES_MINUTES),
            refresh_token=TokenHelper.encode(payload={"sub": "refresh", **current_user.dict()}, expire_period=settings.REFRESH_TOKEN_EXPIRES_MINUTES)
        )
        return response

    async def login(self, onyen: str, autogen_password: str) -> RefreshTokenSchema:
        user = self.session.query(UserModel).filter_by(onyen=onyen).first()
        user_auth = self.session.query(AutoPasswordAuthModel).filter_by(onyen=onyen).first()
        if not user or not user_auth:
            raise UserNotFoundException()
        if not PasswordHelper.verify_password(autogen_password, user_auth.autogen_password_hash):
            raise PasswordDoesNotMatchException()

        return await self._create_user_token(user)
    
    async def create_user_auto_password_auth(self, onyen: str) -> str:
        from src.services import CourseService, KubernetesService
        
        autogen_password = PasswordHelper.generate_password(64)
        autogen_password_hash = PasswordHelper.hash_password(autogen_password)

        user_auth = AutoPasswordAuthModel(
            onyen=onyen,
            autogen_password_hash=autogen_password_hash
        )
        self.session.add(user_auth)
        self.session.commit()

        course = await CourseService(self.session).get_course()
        user = await self.get_user_by_onyen(onyen)
        KubernetesService().create_credential_secret(
            course_name=course.name,
            onyen=onyen,
            password=autogen_password,
            user_type=user.user_type
        )

        return autogen_password

    async def delete_user(
        self,
        onyen: str
    ) -> None:
        from src.services import GiteaService, KubernetesService, CourseService, CleanupService
        
        course = await CourseService(self.session).get_course()
        user = await self.get_user_by_onyen(onyen)

        password = KubernetesService().get_autogen_password(course.name, onyen)
        cleanup_service = CleanupService.User(self.session, user, password)

        KubernetesService().delete_credential_secret(course.name, onyen)
        try:
            await GiteaService(self.session).delete_user(onyen, purge=True)
        except Exception as e:
            await cleanup_service.undo_delete_user(create_password_secret=True)
            raise e

        self.session.delete(user)
        self.session.commit()

        dispatch(DeleteUserCrudEvent(user=user))
